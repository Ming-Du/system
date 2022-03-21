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
from entity.LocInfo import LocInfo
from entity.CommonPara import CommonPara

from threading import Thread
import threading
from concurrent.futures import ThreadPoolExecutor
import json
from entity.CollectVehicleInfo import CollectVehicleInfo
from

### global area
globalLocationPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalLocationPool')
globalTopicHzPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalTopicHzPool')
globalCollectVehicleInfo = CollectVehicleInfo()
globalCommonPara = CommonPara()


class LocationModule:
    def __init__(self):
        pass

    def task_localization(self, pb_msg):
        thread_name = threading.current_thread().getName()
        location = common_localization.Localization()
        location.ParseFromString(pb_msg)
        instanceLocInfoUnit = LocInfo()
        instanceLocInfoUnit.MarkMapPosition_x = location.position.x
        instanceLocInfoUnit.MarkMapPosition_y = location.position.y
        instanceLocInfoUnit.MarkMapPosition_longitude = location.longitude
        instanceLocInfoUnit.MarkMapPosition_latitude = location.latitude
        instanceLocInfoUnit.sec = (location.header.stamp.sec)
        instanceLocInfoUnit.nsec = (location.header.stamp.nsec)

    def localizationCallback(self, msg):
        if msg.size > 0:
            globalLocationPool.submit(self.task_localization, msg.data)

    def addLocalizationListener(self):
        rospy.Subscriber('/localization/global', BinaryData, self.localizationCallback)
