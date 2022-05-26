#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Author: liyuelei liyuelei@zhidaoauto.com
Date: 2022-05-10 16:49:38
LastEditors: liyuelei liyuelei@zhidaoauto.com
LastEditTime: 2022-05-11 23:11:29
FilePath: /catkin_ws/src/system/system_master/sys_test_tools.py
'''
import os
import time
import threading
import rospy
from rospy import Publisher, init_node, rostime
from proto import common_vehicle_state, system_cmd_pb2
from autopilot_msgs.msg import BinaryData
from std_msgs.msg import Int32

# globals
g_pilot_mode = 0

def test_vehicle_state_pub():
    '''
    used for test vehicle state
    '''
    global g_pilot_mode
    pub_hd = Publisher("/chassis/vehicle_state", BinaryData, queue_size=100)
    rt = rospy.Rate(10)

    while not rospy.is_shutdown():
        pub_msg_data = common_vehicle_state.VehicleState()
        pub_msg_data.header.seq          = 1
        pub_msg_data.header.stamp.sec    = rostime.Time.now().secs
        pub_msg_data.header.stamp.nsec   = rostime.Time.now().nsecs
        pub_msg_data.header.frame_id     = "vehicle_state_frame_id"
        pub_msg_data.pilot_mode = g_pilot_mode
        '''
        pub_msg_data.steer_inference = self.local_vehicle_state.steer_inference
        pub_msg_data.brake_inference = self.local_vehicle_state.brake_inference
        pub_msg_data.accel_inference = self.local_vehicle_state.accel_inference
        pub_msg_data.gear_switch_inference = self.local_vehicle_state.gear_switch_inference
        pub_msg_data.location_missing = self.local_vehicle_state.location_missing
        pub_msg_data.trajectory_missing = self.local_vehicle_state.trajectory_missing
        pub_msg_data.chassis_status_missing = self.local_vehicle_state.chassis_status_missing
        pub_msg_data.brake_light_status = self.local_vehicle_state.brake_light_status
        pub_msg_data.pilot_mode_condition_met = self.local_vehicle_state.pilot_mode_condition_met
        '''

        pub_msg_data_str = pub_msg_data.SerializeToString()

        vehicle_msg = BinaryData()
        vehicle_msg.header.seq = 1
        vehicle_msg.header.stamp.secs = rostime.Time.now().secs
        vehicle_msg.header.stamp.nsecs = rostime.Time.now().nsecs
        vehicle_msg.header.frame_id = "system_testtool_frame_id"
        vehicle_msg.name = "system_testtool"
        vehicle_msg.size = len(pub_msg_data_str)
        vehicle_msg.data = pub_msg_data_str

        pub_hd.publish(vehicle_msg)
        rt.sleep()

def test_system_cmd_pub(src, action):
    '''
    used for test system cmd
    '''
    pub_cmd = Publisher("/system_master/SystemCmd", BinaryData, queue_size=10)

    sys_cmd_data = system_cmd_pb2.SystemCmd()
    sys_cmd_data.header.seq          = 1
    sys_cmd_data.header.stamp.sec    = rostime.Time.now().secs
    sys_cmd_data.header.stamp.nsec   = rostime.Time.now().nsecs
    sys_cmd_data.header.frame_id     = "vehicle_state_frame_id"
    sys_cmd_data.src = src
    sys_cmd_data.action = action
    pub_msg_data_str = sys_cmd_data.SerializeToString()

    syscmd_msg = BinaryData()
    syscmd_msg.header.seq = 1
    syscmd_msg.header.stamp.secs = rostime.Time.now().secs
    syscmd_msg.header.stamp.nsecs = rostime.Time.now().nsecs
    syscmd_msg.header.frame_id = "system_testtool_frame_id"
    syscmd_msg.name = "system_testtool"
    syscmd_msg.size = len(pub_msg_data_str)
    syscmd_msg.data = pub_msg_data_str

    pub_cmd.publish(syscmd_msg)

def cmd_recv(ros_msg):
    global g_pilot_mode
    if ros_msg.data:
        g_pilot_mode = 1
    else:
        g_pilot_mode = 0

def test_autopilot_cmd_sub():
    rospy.Subscriber('/autopilot/AutoPilotCmd', Int32, cmd_recv)
    rospy.spin()


if __name__ == '__main__':
    init_node('master_test')
    th1 = threading.Thread(target=test_vehicle_state_pub, name='test as chassis')
    th2 = threading.Thread(target=test_autopilot_cmd_sub, name='test as controller')
    th1.start()
    th2.start()

    try:
        test_system_cmd_pub(system_cmd_pb2.AutoPolit, system_cmd_pb2.StartPilot)
        time.sleep(3)
        test_system_cmd_pub(system_cmd_pb2.AutoPolit, system_cmd_pb2.StopPilot)
        time.sleep(5)
        test_system_cmd_pub(system_cmd_pb2.AutoPolit, system_cmd_pb2.BeginShowMode)
        test_system_cmd_pub(system_cmd_pb2.AutoPolit, system_cmd_pb2.StartPilot)
        time.sleep(2)
        g_pilot_mode = 0
        time.sleep(5)
        test_system_cmd_pub(system_cmd_pb2.AutoPolit, system_cmd_pb2.EndShowMode)

        test_system_cmd_pub(system_cmd_pb2.AutoPolit, system_cmd_pb2.SysReboot)
        time.sleep(5)
        test_system_cmd_pub(system_cmd_pb2.AutoPolit, system_cmd_pb2.StopPilot)
        time.sleep(5)
        test_system_cmd_pub(system_cmd_pb2.AutoPolit, system_cmd_pb2.SysReboot)

    except rospy.ROSInterruptException:
        pass

    time.sleep(10)
    os._exit(0)
