#include <iostream>
#include <thread>
#include <ros/ros.h>

#include "mogo_reporter/mogo_reporter.h"

int main(int argc, char **argv)
{
  ros::init(argc, argv, "mogo_report_test");

  MOGO_MSG_INIT_CFG("mogo_sys");
  std::this_thread::sleep_for(std::chrono::milliseconds(1000));

  MOGO_MSG_REPORT_SRC("test", "ISYS_AUTOPILOT_RUNING");
  MOGO_MSG_REPORT_SRC("test", "IMAP_TRA_LOADED", "123");
  MOGO_MSG_REPORT_SRC("test", "ITELEMATICS_AICLOUD_AUTH_OK");

  MOGO_MSG_REPORT_SRC("test", "EINIT_LOST_FILE", "333");
  MOGO_MSG_REPORT_SRC("test", "EMAP_EXIT_AUTOPILOT_FOR_PLANNING", "444");
  MOGO_MSG_REPORT_SRC("test", "EAGENT_MASTER_COMMAND_HANDLER_FAILED");

  MOGO_MSG_REPORT("EMAP_CAN_ADAPTER_NO_CHASSIS_INFO");
  MOGO_MSG_REPORT("ESYS_TOPIC_FREQ_DROPED");
  MOGO_MSG_REPORT("EAGENT_MASTER_COMMAND_HANDLER_FAILED");

  ros::spin();

  return 0;
}