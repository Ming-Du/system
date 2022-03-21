#!/usr/bin/env python2
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
import proto.mogo_report_msg_pb2 as comon_mogo_report_msg_pb2
from entity.LocInfo import LocInfo
from entity.CommonPara import CommonPara

from threading import Thread
import threading
from concurrent.futures import ThreadPoolExecutor
import json
from entity.CollectVehicleInfo import CollectVehicleInfo
import proto.mogo_report_msg_pb2 as common_mogo_report_msg_pb2
import proto.monitor_msg_pb2 as common_monitor_msg_pb2
import proto.monitor_topic_hz_pb2 as monitor_topic_hz_pb2

### global area
globalTopicHzPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalTopicHzPool')
globalTopicMsgPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalTopicMsgPool')
globalCollectVehicleInfo = CollectVehicleInfo()
globalCommonPara = CommonPara()
rDictHzTable = {}

rospy.init_node("simu_hz")
pub_hz = rospy.Publisher("/autopilot_info/report_topic_hz", BinaryData, queue_size=100)
pub_msg = rospy.Publisher("/autopilot_info/report_msg_info", BinaryData, queue_size=100)

seq_hz = 1
def simu_hz():
    print "enter send simu_hz"
    global seq_hz
    seq_hz =2
    rosMsg = BinaryData()
    pbTopicHz = common_log_reslove_pb2.PubLogInfo()
    pbTopicHz.header.seq =  int(seq_hz)
    pbTopicHz.header.stamp.sec  = int(seq_hz)
    pbTopicHz.header.stamp.nsec = int(seq_hz)
    pbTopicHz.header.frame_id = "frame_id"
    pbTopicHz.header.module_name = "module_name"
    pbTopicHz.start_stamp = int(seq_hz)*1000+int(seq_hz)
    pbTopicHz.end_stamp = int(seq_hz)*1000+int(seq_hz)+1
    elemHz = pbTopicHz.topic_hz.add()
    elemHz.name = "/app1"
    elemHz.hz = seq_hz
    elemHz = pbTopicHz.topic_hz.add()
    elemHz.name = "/app2"
    elemHz.hz = seq_hz
    elemHz = pbTopicHz.topic_hz.add()
    elemHz.name = "/app3"
    elemHz.hz = seq_hz
    strBuffer = pbTopicHz.SerializeToString()
    rosMsg.data = strBuffer
    rosMsg.size = len(strBuffer)
    pub_hz.publish(rosMsg)
    seq_hz = seq_hz + 1
    print "after send simu_hz"


def simu_mesg():
    print "enter send simu_mesg"
    pbOriginMsg = common_mogo_report_msg_pb2.MogoReportMessage()
    pbOriginMsg.timestamp.sec = rospy.rostime.Time.now().secs
    pbOriginMsg.timestamp.nsec = rospy.rostime.Time.now().nsecs

    pbOriginMsg.src = "src_app_1"
    pbOriginMsg.level = "info"
    pbOriginMsg.msg = "define mesg 1 xxxx "
    pbOriginMsg.code = "SRC_APP_!_ERROR_CODE_!"

    pbOriginMsg.result.append("result1")
    pbOriginMsg.result.append("result2")

    pbOriginMsg.actions.append("action1")
    pbOriginMsg.actions.append("action2")
    strBuffer = pbOriginMsg.SerializeToString()

    rosMessage = BinaryData()
    rosMessage.data = strBuffer
    rosMessage.size = len(strBuffer)
    pub_msg.publish(rosMessage)
    print "finish  send simu_mesg"


if __name__ == "__main__":
    try:
        while True:
            simu_mesg()
            simu_hz()
            time.sleep(3)
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
