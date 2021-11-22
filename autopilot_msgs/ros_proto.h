#pragma once

#include <ros/ros.h>
#include <autopilot_msgs/BinaryData.h>
#include <common/include/pb_utils.h>

template <class ProtoMessage>
void RosToProto(const autopilot_msgs::BinaryData& ros_msg, 
    ProtoMessage& proto_msg)
{
    if (ros_msg.name == proto_msg.GetTypeName())
    {
        proto_msg.mutable_header()->set_seq(ros_msg.header.seq);
        proto_msg.mutable_header()->mutable_stamp()->set_sec(ros_msg.header.stamp.sec);
        proto_msg.mutable_header()->mutable_stamp()->set_nsec(ros_msg.header.stamp.nsec);
        proto_msg.mutable_header()->set_frame_id(ros_msg.header.frame_id);
        common::DeserializeProto(proto_msg, ros_msg.data);
    }
    else
    {
        ROS_ERROR("RosToProto: %s -> %s", ros_msg.name.c_str(), proto_msg.GetTypeName().c_str());
    }
    
}

template <class ProtoMessage>
void ProtoToRos(const ProtoMessage& proto_msg, 
    autopilot_msgs::BinaryData& ros_msg)
{
    ros_msg.header.seq = proto_msg.header().seq();
    ros_msg.header.stamp.sec = proto_msg.header().stamp().sec();
    ros_msg.header.stamp.nsec = proto_msg.header().stamp().nsec();
    ros_msg.header.frame_id = proto_msg.header().frame_id();
    ros_msg.name = proto_msg.GetTypeName();
    common::SerializeProto(proto_msg, ros_msg.data);
    ros_msg.size = ros_msg.data.size();
}

template<class ProtoMessage>
class ProtoPublisher
{
private:
    autopilot_msgs::BinaryData data;
    uint32_t seq;
public:
    ProtoPublisher() : seq(1) {}
    void publish(ros::Publisher& pub, const ProtoMessage& msg)
    {
        ProtoToRos<ProtoMessage>(msg, data);
        data.header.stamp = ros::Time::now();
        data.header.seq = seq++;
        pub.publish(data);
    }
};


