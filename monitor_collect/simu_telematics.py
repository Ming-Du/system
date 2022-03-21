#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from random import random

import rospy
import rosnode
import rosparam
import os
from threading import Thread

import std_msgs
from std_msgs.msg import String
from rospy import init_node, Subscriber
import json
# import psutil
import collections
import sys
# import simplejson
import logging
import re
import time
import datetime

from autopilot_msgs.msg import BinaryData
import proto.localization_pb2 as common_localization
import proto.vehicle_state_pb2 as common_vehicle_state_pb2
import proto.log_reslove_pb2 as common_log_reslove_pb2
import proto.mogo_report_msg_pb2  as comon_mogo_report_msg_pb2
from  entity.LocInfo import  LocInfo
from entity.CommonPara import  CommonPara

from threading import Thread
import threading
from concurrent.futures import ThreadPoolExecutor
import json
from entity.CollectVehicleInfo import   CollectVehicleInfo
import proto.mogo_report_msg_pb2  as common_mogo_report_msg_pb2
import proto.monitor_msg_pb2 as  common_monitor_msg_pb2
import proto.monitor_topic_hz_pb2 as monitor_topic_hz_pb2


### global area
globalTopicHzPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalTopicHzPool')
globalTopicMsgPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalTopicMsgPool')
globalCollectVehicleInfo  = CollectVehicleInfo()
globalCommonPara = CommonPara()
globalPubToTelematicsInfo=rospy.Publisher("/autopilot_info/report_msg_info",BinaryData,queue_size=100)
globalPubToTelematicsError=rospy.Publisher("/autopilot_info/report_msg_error",BinaryData,queue_size=100)
rDictHzTable = {}
dictSubScriptHzItem =  {}

def topicHzRecvCallback(msg):
    print "==========================recv from  channel /cloud_debug/report_topic_hz "
    if msg.size > 0:
        pbMonitorHzWidthCarInfo = monitor_topic_hz_pb2.MonitorTopicHz()
        pbMonitorHzWidthCarInfo.ParseFromString(msg.data)
        global rDictHzTable
        for elemHz in pbMonitorHzWidthCarInfo.pLogInfo.topic_hz:
            print "topicname:%s " %(elemHz.name)
            print "hz:%d" %(elemHz.hz)
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.seq:%d" % (pbMonitorHzWidthCarInfo.pLogInfo.header.seq)
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.sec:%d" % (pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.sec)
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.nsec:%d" % (pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.nsec)
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.frame_id:%s " % (pbMonitorHzWidthCarInfo.pLogInfo.header.frame_id)
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.module_name:%s" % (pbMonitorHzWidthCarInfo.pLogInfo.header.module_name)
        print "pbMonitorHzWidthCarInfo.pLogInfo.start_stamp:%f" % (pbMonitorHzWidthCarInfo.pLogInfo.start_stamp)
        print "pbMonitorHzWidthCarInfo.pLogInfo.end_stamp:%f" % (pbMonitorHzWidthCarInfo.pLogInfo.end_stamp)
def MessageRecvCallback(msg):
    print "========================================recv from  channel /cloud_debug/report_msg_info"
    if msg.size > 0:
        pbRecvMsg = common_monitor_msg_pb2.MonitorMsg()
        pbRecvMsg.ParseFromString(msg.data)
        print  "pbRecvMsg.carinfo.car_type:%s" %(pbRecvMsg.carinfo.car_type)
        print  "pbRecvMsg.carinfo.car_type:%s " %(pbRecvMsg.carinfo.code_version)
        print  "pbRecvMsg.carinfo.car_type:%s" %(pbRecvMsg.carinfo.car_plate)
        print  "pbRecvMsg.timestamp.sec:%d" %(pbRecvMsg.reportmsg.timestamp.sec)
        print  "pbRecvMsg.reportmsg.timestamp.sec:%d" % (pbRecvMsg.reportmsg.timestamp.sec)
        print  "pbRecvMsg.reportmsg.timestamp.nsec:%d" % (pbRecvMsg.reportmsg.timestamp.nsec)
        print  "pbRecvMsg.reportmsg.src:%s" %(pbRecvMsg.reportmsg.src)
        print  "pbRecvMsg.reportmsg.level:%s" %(pbRecvMsg.reportmsg.level)
        print  "pbRecvMsg.reportmsg.msg:%s" %(pbRecvMsg.reportmsg.msg)
        print  "pbRecvMsg.reportmsg.code:%s" %(pbRecvMsg.reportmsg.code)

def addLocalizationListener():
    rospy.Subscriber("/cloud_debug/report_msg_error",BinaryData,MessageRecvCallback)
    rospy.Subscriber("/cloud_debug/report_msg_info", BinaryData, MessageRecvCallback)
    rospy.Subscriber("/cloud_debug/report_topic_hz",BinaryData,topicHzRecvCallback)

def main():
    # initial node
    globalCommonPara.initPara()
    rospy.init_node('simu_telematics', anonymous=True)
    # add listener
    addLocalizationListener()
    ## wait msg
    rospy.spin()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
