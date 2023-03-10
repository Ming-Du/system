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
#include <ros/time.h>

#include <yaml-cpp/yaml.h>

#include "common/include/pb_utils.h"
#include "common/proto/mogo_report_msg.pb.h"
#include "autopilot_msgs/BinaryData.h"

#define MOGO_RPT_MSG_INFO "info"
#define MOGO_RPT_MSG_ERROR "error"
#define MOGO_RPT_INFO_TOPIC "/autopilot_info/report_msg_info"
#define MOGO_RPT_ERROR_TOPIC "/autopilot_info/report_msg_error"

#define MOGO_MSG_CONFIG_DIR "/nodes/"

namespace mogo
{
  struct ReportMsgEntity
  {
    std::string level;
    std::string code;
    std::string msg;
    std::vector<std::string> results;
    std::vector<std::string> actions;
    double last_timestamp;
  };

  static std::mutex s_init_locker = {};
  static bool s_is_init = false;
  static std::map<std::string, ReportMsgEntity> s_msg_map = {};

  static ros::NodeHandle *s_nh;
  static ros::Publisher s_pub_info;
  static ros::Publisher s_pub_error;

  static bool getYamlFiles(const std::string &path, std::vector<std::string> &files)
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
        std::string::size_type pos_end = filename.find(".yaml");
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

  static bool addMessageCode(const YAML::Node &node, const std::string &level)
  {
    if (!node["code"].IsDefined() || node["code"].IsNull() ||
        !node["msg"].IsDefined() || node["msg"].IsNull())
    {
      return false;
    }

    ReportMsgEntity report_msg;
    report_msg.last_timestamp = 0.0;
    report_msg.level = level;
    report_msg.code = node["code"].as<std::string>();
    report_msg.msg = node["msg"].as<std::string>();

    const YAML::Node &result_node = node["result"];
    if (result_node.IsDefined() && result_node.IsSequence())
    {
      for (std::size_t i = 0; i < result_node.size(); i++)
      {
        if (!result_node[i].IsNull())
        {
          report_msg.results.push_back(result_node[i].as<std::string>());
        }
      }
    }

    const YAML::Node &action_node = node["action"];
    if (action_node.IsDefined() && action_node.IsSequence())
    {
      for (std::size_t i = 0; i < action_node.size(); i++)
      {
        if (!action_node[i].IsNull())
        {
          report_msg.actions.push_back(action_node[i].as<std::string>());
        }
      }
    }

    s_msg_map.insert(std::make_pair(report_msg.code, report_msg));
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

    std::string config_dir = ros::package::getPath("mogo_messages") + MOGO_MSG_CONFIG_DIR;
    std::vector<std::string> files;
    std::string config_path;

    if (!getYamlFiles(config_dir, files))
    {
      ROS_ERROR("MessageReporter_init: fail to open config dir %s", config_dir.c_str());
      return false;
    }

    for (const auto &it : files)
    {
      if (node_name.find(it) != std::string::npos)
      {
        config_path = config_dir + it + ".yaml";
        break;
      }
    }

    if (config_path.empty())
    {
      ROS_ERROR("MessageReporter_init: fail to open config dir %s", config_dir.c_str());
      return false;
    }

    YAML::Node config;
    try
    {
      config = YAML::LoadFile(config_path);
    }
    catch (std::exception &e)
    {
      ROS_ERROR("MessageReporter_init: fail to load config file [%s], msg: [%s]", config_path.c_str(), e.what());
      return false;
    }

    int info_num = 0;
    int err_num = 0;
    try
    {
      const YAML::Node &info_node = config["info"];
      if (info_node.IsDefined() && info_node.IsSequence())
      {
        for (std::size_t i = 0; i < info_node.size(); i++)
        {
          if (addMessageCode(info_node[i], MOGO_RPT_MSG_INFO))
          {
            info_num++;
          }
        }
      }
    }
    catch (const std::exception &e)
    {
      ROS_ERROR("MessageReporter_init: fail to read info messages [%s], msg: [%s]", config_path.c_str(), e.what());
      return false;
    }

    try
    {
      const YAML::Node &error_node = config["error"];
      if (error_node.IsDefined() && error_node.IsSequence())
      {
        for (std::size_t i = 0; i < error_node.size(); i++)
        {
          if (addMessageCode(error_node[i], MOGO_RPT_MSG_ERROR))
          {
            err_num++;
          }
        }
      }
    }
    catch (std::exception &e)
    {
      ROS_ERROR("MessageReporter_init: fail to load error messages [%s], msg: [%s]", config_path.c_str(), e.what());
      return false;
    }

    ROS_INFO("MessageReporter_init: success to load config from [%s]. infos: %d, errors: %d", config_path.c_str(), info_num, err_num);
    s_is_init = true;
    return true;
  }

  bool MessageReporter::publish_src(const std::string &src, const std::string &code, const std::string &msg, double span_sec)
  {
    if (!s_is_init)
    {
      ROS_WARN("MessageReporter_publish: reporter is not inited, ignore");
      return false;
    }
    auto iter = s_msg_map.find(code);
    if (iter == s_msg_map.end())
    {
      ROS_WARN("MessageReporter_publish: unknow code[%s], ignore", code.c_str());
      return false;
    }

    ros::Time now = ros::Time::now();
    if (span_sec > 0.0 && now.toSec() - iter->second.last_timestamp < span_sec)
    {
      ROS_WARN("MessageReporter_publish: code[%s] is published in %0.1f sec, ignore", code.c_str(), span_sec);
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

    for (const auto &it : iter->second.results)
    {
      report_msg.add_result(it);
    }
    for (const auto &it : iter->second.actions)
    {
      report_msg.add_actions(it);
    }

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
      ros::Duration(0.1).sleep();
      publish(it.first);
    }
  }
}