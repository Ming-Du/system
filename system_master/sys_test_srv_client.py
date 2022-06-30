#!/usr/bin/env python
# coding=utf-8
"""
#@
#@   ┏┓　　　┏┓
#@ ┏┛┻━━━┛┻┓
#@ ┃　　　　　　　┃
#@ ┃　　　━　　　┃
#@ ┃　＞　　　＜　┃
#@ ┃　　　　　　　┃
#@ ┃...　⌒　...　┃
#@ ┃　　　　　　　┃
#@ ┗━┓　　　┏━┛
#@     ┃　　　┃　
#@     ┃　　　┃
#@     ┃　　　┃
#@     ┃　　　┃  神兽保佑
#@     ┃　　　┃  代码无bug　　
#@     ┃　　　┃
#@     ┃　　　┗━━━┓
#@     ┃　　　　　　　┣┓
#@     ┃　　　　　　　┏┛
#@     ┗┓┓┏━┳┓┏┛
#@       ┃┫┫　┃┫┫
#@       ┗┻┛　┗┻┛
#@
#@Author: Orange
#@Date: 2022-06-02 14:31:15
#@FilePath: /catkin_ws/src/system/system_master/sys_test_srv_client.py
#@Email: liyuelei@zhidaoauto.com
#@LastEditTime: 2022-06-02 14:47:37
"""


import rospy
from autopilot_msgs.srv import StatusQuery, StatusQueryResponse
from autopilot_msgs.msg import BinaryData
from proto import system_status_info_pb2


def get_system_status():
    rospy.wait_for_service('query_master_status')
    try:
        client_handle = rospy.ServiceProxy('query_master_status', StatusQuery)
        resp = client_handle().status_msg
        #import pdb; pdb.set_trace()

        print("reveice response from {}, size={}:".format(resp.name, resp.size))
        if resp.size:
            RecvMsg = system_status_info_pb2.StatusInfo()
            RecvMsg.ParseFromString(resp.data)

            print("\tsys_state:\t{}".format(RecvMsg.sys_state))
            for health_info in RecvMsg.health_info:
                print("\tname:\t{}".format(health_info.name))
                print("\t\tstate:\t{}".format(health_info.state))
                print("\t\tcode:\t{}".format(health_info.code))
                print("\t\tdesc:\t{}".format(health_info.desc))

    except rospy.ServiceException as e:
        print ("Service call failed: {}".format(e))


if __name__=='__main__':
    get_system_status()
