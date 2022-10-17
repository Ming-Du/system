#pragma once

#include <string>
#include <ros/this_node.h>

#define MOGO_REPORTER_SPAN_SEC 3.0

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

    bool publish(const std::string &code, const std::string &msg = "", double span_sec = MOGO_REPORTER_SPAN_SEC)
    {
      return publish_src(ros::this_node::getName(), code, msg, span_sec);
    }
    bool publish_src(const std::string &src, const std::string &code, const std::string &msg = "", double span_sec = MOGO_REPORTER_SPAN_SEC);

    void test_all();

  private:
    MessageReporter();
    MessageReporter(const MessageReporter &) = delete;
    MessageReporter &operator=(const MessageReporter &) = delete;
  };
}

/**
 * 初始化事件报告器
 */
#define MOGO_MSG_INIT() mogo::MessageReporter::instance().init()
#define MOGO_MSG_INIT_CFG(name) mogo::MessageReporter::instance().init(name)

/**
 * MOGO_MSG_REPORT("事件码字符串");
 * MOGO_MSG_REPORT("事件码字符串", "附带数据字符串");
 * MOGO_MSG_REPORT("事件码字符串", "附带数据字符串", 3.0); // 事件报告最小间隔时间, 如果不添加第三个参数，默认是 MOGO_REPORTER_SPAN_SEC
 *
 * 使用事件码枚举的方式即将弃用，请使用事件码字符串上报！！！
 * 弃用: MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::EMAP_CAN_ADAPTER_NO_CHASSIS_INFO)
 * 推荐: MOGO_MSG_REPORT("EMAP_CAN_ADAPTER_NO_CHASSIS_INFO")
 */
#define MOGO_MSG_REPORT(code, ...) mogo::MessageReporter::instance().publish(code, ##__VA_ARGS__)
#define MOGO_MSG_REPORT_SRC(src, code, ...) mogo::MessageReporter::instance().publish_src(src, code, ##__VA_ARGS__)