#include <stdio.h>
#include <stdlib.h>
#include <ros/ros.h>

#include "mogo_reporter/mogo_reporter.h"

int main(int argc, char **argv)
{
  if (argc < 2)
  {
    fprintf(stderr, "Usage: rosrun mogo_reporter mogo_report_test_all <config_name>\n");
    exit(EXIT_FAILURE);
  }

  ros::init(argc, argv, "mogo_report_test");

  MOGO_MSG_INIT_CFG(argv[1]);

  ros::Duration(1.0).sleep();

  mogo::MessageReporter::instance().test_all();

  ros::spin();

  exit(EXIT_SUCCESS);
}