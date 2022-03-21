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
globalPubToTelematicsInfo = rospy.Publisher("/autopilot_info/report_msg_info", BinaryData, queue_size=100)
globalPubToTelematicsError = rospy.Publisher("/autopilot_info/report_msg_error", BinaryData, queue_size=100)
rDictHzTable = {}

pub = rospy.Publisher("/agent/info/networkinfo", BinaryData, queue_size=10)


def processNetworkInfo():

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
    pub.publish(rosMessage)




def main():
    rospy.init_node('', anonymous=True)


if __name__ == "__main__":
    try:
        simu_mesg()
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
