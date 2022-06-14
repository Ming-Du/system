#include "mogo_reporter/mogo_reporter.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <iostream>
#include <unistd.h>
#include <dirent.h>
#include <map>
#include <mutex>
#include <vector>
#include <memory>

#include <ros/node_handle.h>
#include <ros/package.h>

#include "common/include/pb_utils.h"
#include "common/proto/mogo_report_msg.pb.h"
#include "autopilot_msgs/BinaryData.h"

#define MOGO_RPT_MSG_INFO "info"
#define MOGO_RPT_MSG_ERROR "error"
#define MOGO_RPT_INFO_TOPIC "/autopilot_info/report_msg_info"
#define MOGO_RPT_ERROR_TOPIC "/autopilot_info/report_msg_error"

namespace mogo
{
  struct ReportMsgInternal
  {
    std::string level;
    std::string code;
    std::string msg;
    ::google::protobuf::RepeatedPtrField<::std::string> results;
    ::google::protobuf::RepeatedPtrField<::std::string> actions;
    double last_timestamp;
  };

  static std::mutex s_init_locker = {};
  static bool s_is_init = false;
  static std::map<mogo_msg::ReportMsgCode, ReportMsgInternal> s_msg_map = {};

  static ros::NodeHandle *s_nh;
  static ros::Publisher s_pub_info;
  static ros::Publisher s_pub_error;

  static bool getFiles(const std::string &path, std::vector<std::string> &files)
  {
    DIR *dir;
    struct dirent *ptr;

    if ((dir = opendir(path.c_str())) == NULL)
    {
      return false;
    }

    while ((ptr = readdir(dir)) != NULL)
    {
      if (ptr->d_type == DT_REG)
      {
        std::string filename(ptr->d_name);
        std::string::size_type pos_end = filename.find(".pb");
        {
          if (pos_end == filename.npos)
          {
            continue;
          }
        }
        files.push_back(filename.substr(0, pos_end));
      }
    }
    closedir(dir);
    return true;
  }

  MessageReporter::MessageReporter()
  {
    s_nh = new ros::NodeHandle;
    s_pub_info = s_nh->advertise<autopilot_msgs::BinaryData>(MOGO_RPT_INFO_TOPIC, 10);
    s_pub_error = s_nh->advertise<autopilot_msgs::BinaryData>(MOGO_RPT_ERROR_TOPIC, 10);
  }

  MessageReporter::~MessageReporter()
  {
    s_nh->shutdown();
    delete s_nh;
  }

  bool MessageReporter::init(const std::string &cfg_name)
  {
    std::lock_guard<std::mutex> locker(s_init_locker);
    if (s_is_init)
    {
      return true;
    }

    std::string node_name;
    if (cfg_name.empty())
    {
      node_name = ros::this_node::getName();
      auto pos_begin = node_name.rfind('/');
      if (pos_begin != std::string::npos && pos_begin + 1 < node_name.size())
      {
        node_name = node_name.substr(pos_begin + 1);
      }
    }
    else
    {
      node_name = cfg_name;
    }

    std::string config_dir = ros::package::getPath("mogo_reporter") + "/config/";
    std::vector<std::string> files;
    std::string config_path;

    if (!getFiles(config_dir, files))
    {
      ROS_ERROR("MessageReporter_init: fail to open config dir %s", config_dir.c_str());
      return false;
    }

    for (const auto &it : files)
    {
      if (node_name.find(it) != std::string::npos)
      {
        config_path = config_dir + it + ".pb";
        break;
      }
    }

    if (config_path.empty())
    {
      ROS_ERROR("MessageReporter_init: fail to find proto config %s from %s", node_name.c_str(), config_dir.c_str());
      return false;
    }
    ROS_INFO("MessageReporter_init: find proto config file: %s", config_path.c_str());

    mogo_msg::ReportMsgList report_msg_list;
    if (!common::GetProtoFromFile(config_path, report_msg_list))
    {
      ROS_ERROR("MessageReporter_init: fail to get proto from %s", config_path.c_str());
      return false;
    }
    ROS_INFO("MessageReporter_init: success to get config. infos: %d, errors: %d", report_msg_list.info_size(), report_msg_list.error_size());

    auto infos = report_msg_list.mutable_info();
    for (auto it = infos->begin(); it != infos->end(); ++it)
    {
      ReportMsgInternal report_msg;
      report_msg.level = MOGO_RPT_MSG_INFO;
      report_msg.code = mogo_msg::ReportMsgCode_Name(it->code());
      report_msg.msg = it->msg();
      report_msg.results.CopyFrom(it->result());
      report_msg.actions.CopyFrom(it->action());
      report_msg.last_timestamp = 0.0;
      s_msg_map.insert(std::make_pair(it->code(), report_msg));
    }

    auto errors = report_msg_list.mutable_error();
    for (auto it = errors->begin(); it != errors->end(); ++it)
    {
      ReportMsgInternal report_msg;
      report_msg.level = MOGO_RPT_MSG_ERROR;
      report_msg.code = mogo_msg::ReportMsgCode_Name(it->code());
      report_msg.msg = it->msg();
      report_msg.results.CopyFrom(it->result());
      report_msg.actions.CopyFrom(it->action());
      report_msg.last_timestamp = 0.0;
      s_msg_map.insert(std::make_pair(it->code(), report_msg));
    }

    s_is_init = true;
    return true;
  }

  bool MessageReporter::publish(std::string src, mogo_msg::ReportMsgCode code, const std::string &msg, double span_sec)
  {
    if (!s_is_init)
    {
      ROS_WARN("MessageReporter_publish: reporter is not inited, ignore");
      return false;
    }
    auto iter = s_msg_map.find(code);
    if (iter == s_msg_map.end())
    {
      ROS_WARN("MessageReporter_publish: unknow code[%s], ignore", mogo_msg::ReportMsgCode_Name(code).c_str());
      return false;
    }

    ros::Time now = ros::Time::now();
    if (span_sec > 0.0 && now.toSec() - iter->second.last_timestamp < span_sec)
    {
      ROS_WARN("MessageReporter_publish: code[%s] is published in %0.1f sec, ignore", mogo_msg::ReportMsgCode_Name(code).c_str(), span_sec);
      return false;
    }

    mogo_msg::MogoReportMessage report_msg;
    auto t = report_msg.mutable_timestamp();
    t->set_sec(now.sec);
    t->set_nsec(now.nsec);

    report_msg.set_src(src);
    report_msg.set_level(iter->second.level);
    report_msg.set_code(iter->second.code);

    if (msg.empty())
    {
      if (!iter->second.msg.empty())
      {
        report_msg.set_msg(iter->second.msg);
      }
    }
    else
    {
      if (iter->second.msg.empty())
      {
        report_msg.set_msg(msg);
      }
      else
      {
        std::string merge = iter->second.msg + "\n" + msg;
        report_msg.set_msg(merge);
      }
    }

    report_msg.mutable_actions()->CopyFrom(iter->second.actions);
    report_msg.mutable_result()->CopyFrom(iter->second.results);

    autopilot_msgs::BinaryData ros_msg;
    ros_msg.header.stamp = now;
    ros_msg.header.frame_id = "mogo_reporter";
    ros_msg.name = report_msg.GetTypeName();
    common::SerializeProto(report_msg, ros_msg.data);
    ros_msg.size = ros_msg.data.size();

    bool is_err = (iter->second.level == MOGO_RPT_MSG_ERROR);
    if (is_err)
    {
      s_pub_error.publish(ros_msg);
    }
    else
    {
      s_pub_info.publish(ros_msg);
    }

    iter->second.last_timestamp = now.toSec();
    return true;
  }

  void MessageReporter::test_all()
  {
    for (auto &it : s_msg_map)
    {
      publish(it.first);
    }
  }
}