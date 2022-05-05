#pragma once

#include <string>
#include <ros/this_node.h>
#include "mogo_report_codes.pb.h"

namespace mogo
{
  class MessageReporter
  {
  public:
    static MessageReporter &instance()
    {
      static MessageReporter reporter;
      return reporter;
    }

    ~MessageReporter();

    bool init(const std::string &cfg_name = "");

    bool publish(mogo_msg::ReportMsgCode code, const std::string &msg = "")
    {
      return publish(ros::this_node::getName(), code, msg);
    }
    bool publish(std::string src, mogo_msg::ReportMsgCode code, const std::string &msg = "");

  private:
    MessageReporter();
    MessageReporter(const MessageReporter &) = delete;
    MessageReporter &operator=(const MessageReporter &) = delete;
  };
}

#define MOGO_MSG_INIT() mogo::MessageReporter::instance().init()
#define MOGO_MSG_INIT_CFG(name) mogo::MessageReporter::instance().init(name)

#define MOGO_MSG_REPORT(code, ...) mogo::MessageReporter::instance().publish(code, ##__VA_ARGS__)
#define MOGO_MSG_REPORT_SRC(src, code, ...) mogo::MessageReporter::instance().publish(src, code, ##__VA_ARGS__)