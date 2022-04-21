#include <iostream>
#include <thread>
#include <ros/ros.h>

#include "mogo_reporter/mogo_reporter.h"

int main(int argc, char **argv)
{
  ros::init(argc, argv, "mogo_report_test");

  MOGO_MSG_INIT_CFG("telematics");
  std::this_thread::sleep_for(std::chrono::milliseconds(1000));

  MOGO_MSG_REPORT_SRC("test", mogo_msg::ReportMsgCode::ITELEMATICS_AUTOPILOT_CMD_RECEIVED);
  MOGO_MSG_REPORT_SRC("test", mogo_msg::ReportMsgCode::ITELEMATICS_AUTOPILOT_CMD_FORWARDED, "123");
  MOGO_MSG_REPORT_SRC("test", mogo_msg::ReportMsgCode::ITELEMATICS_AICLOUD_AUTH_OK);

  MOGO_MSG_REPORT_SRC("test", mogo_msg::ReportMsgCode::ETELEMATICS_START_AUTO_PILOT_FAILED, "333");
  MOGO_MSG_REPORT_SRC("test", mogo_msg::ReportMsgCode::ETELEMATICS_PAD_SEND_ERROR, "444");
  MOGO_MSG_REPORT_SRC("test", mogo_msg::ReportMsgCode::ETELEMATICS_PAD_RECV_ERROR);

  MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::ETELEMATICS_START_AUTO_PILOT_FAILED);
  MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::ITELEMATICS_AUTOPILOT_CMD_RECEIVED);
  MOGO_MSG_REPORT(mogo_msg::ReportMsgCode::ETELEMATICS_PAD_RECV_ERROR);

  ros::spin();

  return 0;
}