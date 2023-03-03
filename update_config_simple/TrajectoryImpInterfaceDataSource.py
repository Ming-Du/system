#!/usr/bin/env python
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d]' '- %(levelname)s: %(message)s',
                    level=logging.INFO)
logging.debug('debug message')
import os
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor
import common.message_pad_pb2 as common_message_pad_pb2

import rospy

from InterfaceDataSource import InterfaceDataSource
from Job import Job
from JobItem import JobItem
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool

from CacheUtils import CacheUtils
from CommonUtilsReadFile import CommonUtilsReadFile
from CommonPara import CommonPara
from CommonHttpUtils import CommonHttpUtils
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool
from EnumDataSourceType import EnumDataSourceType
from CommonUtilsCompare import CommonUtilsCompare
from EnumJobType import EnumJobType

import std_msgs
from std_msgs.msg import String
from rospy import init_node, Subscriber
import json
from autopilot_msgs.msg import BinaryData
from EnumJobType import EnumJobType
import common.trajectory_agent_sync_status_pb2 as common_trajectory_agent_sync_status_pb2
import common.message_pad_pb2 as common_message_pad_pb2

instanceCommonUtils = CommonUtilsCompare()
instanceReadConfigFile = CommonUtilsReadFile()
instanceScheduler = CommonSchedulerImpInterfaceTaskSchedulingPool()
instanceCacheUtils = CacheUtils("/home/mogo/data/trajectory_agent_cache_record.json")

globalProcessRequestPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ProcessRequestPool')

globalPubToSystemMasterStatus = rospy.Publisher("/trajectory_agent/cmd/status", BinaryData, queue_size=1000)


class TrajectoryImpInterfaceDataSource(InterfaceDataSource):
    strUrlList = None
    strUrlSync = None
    mScheduler = None
    mEnumDataSourceType = None
    mCacheUtils = None
    mStrConfigFileName = None
    mCommonPara = None
    mInterVal = None

    def __init__(self):
        pass

    def setScheduler(self, instanceScheduler):
        pass

    def setCacheUtils(self, instanceCacheUtil):
        pass

    def getModuleName(self):
        pass

    def getVersion(self):
        pass

    def configure(self):
        pass

    def init_module(self):
        pass

    def destroy_module(self):
        pass

    def transaction(self, msg):
        pass

    def process_topic(self, strTopicName, msg):
        pass

    def process_cycle(self, dictParameter):
        pass

    def process_startup(self, dictParameter):
        pass

    def getNeedUpdateFile(self, refJob):
        pass

    def pushJobScheduler(self, refDataSource, refJob):
        pass

    def schedulerFinishAction(self, refJob):
        pass

    def checkAtomicFeature(self, refJob):
        pass

    def install_stage_path(self, refJob):
        pass

    def install_dst_path(self, refJob):
        pass

    def write_cache_file(self, refJob):
        pass

    def notify_pad(self, refJob):
        pass

    def notify_cloud(self, refJob):
        pass

    def write_event(self, refJob):
        pass

    def getTimeval(self):
        pass
