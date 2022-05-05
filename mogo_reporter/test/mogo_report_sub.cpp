#include <iostream>
#include <ros/ros.h>

#include "mogo_reporter/mogo_reporter.h"
#include "autopilot_msgs/BinaryData.h"
#include "common/include/pb_utils.h"
#include "common/proto/mogo_report_msg.pb.h"

void test_callback(const autopilot_msgs::BinaryData::ConstPtr &msg)
{
  mogo_msg::MogoReportMessage report_msg;
  common::DeserializeProto(report_msg, msg->data);
  std::cout << "====== " << msg->header.seq << " ======" << std::endl;
  std::cout << "timestamp: " << report_msg.timestamp().sec() << "," << report_msg.timestamp().nsec()
            << "\nsrc: " << report_msg.src()
            << "\nlevel: " << report_msg.level()
            << "\nmsg: " << report_msg.msg()
            << "\ncode: " << report_msg.code()
            << "\nresult: " << report_msg.result().size()
            << "\nactions: " << report_msg.actions().size()
            << std::endl;
}

int main(int argc, char **argv)
{
  ros::init(argc, argv, "mogo_report_sub");
  ros::NodeHandle nh;
  ros::Subscriber sub_info = nh.subscribe("/autopilot_info/report_msg_error", 10, test_callback);
  ros::Subscriber sub_error = nh.subscribe("/autopilot_info/report_msg_info", 10, test_callback);

  ros::spin();

  return 0;
}