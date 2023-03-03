#!/usr/bin/env python
# -*- coding: utf-8 -*-
import commands
import signal
from concurrent.futures import ThreadPoolExecutor

import threading
import traceback
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
import collections
import sys
import logging
import re
import time
import datetime
from os import path, access, R_OK
import os, sys, stat
from CommonHttpUtils import CommonHttpUtils



from autopilot_msgs.msg import BinaryData
import common.localization_pb2 as common_localization
import common.vehicle_state_pb2 as common_vehicle_state_pb2
import common.system_pilot_mode_pb2 as common_system_pilot_mode_pb2
from entity.LocInfo import LocInfo
from entity.CommonPara import CommonPara
import common.message_pad_pb2 as common_message_pad
import InterfaceDataSource
from ConfigImpInterfaceDataSource import ConfigImpInterfaceDataSource
from HdMapAgentImpInterfaceDataSource import HdMapAgentImpInterfaceDataSource
from DfTrajectoryImpInterfaceDataSource import DfTrajectoryImpInterfaceDataSource
from AiModelImpInterfaceDataSource import AiModelImpInterfaceDataSource
from SlamMapImpInterfaceDataSource import SlamMapImpInterfaceDataSource
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool
from CommonTriggerImpInterfaceTrigger import CommonTriggerImpInterfaceTrigger
from CommonSimpleSchedulerImpInterfaceTaskSchedulingPool import CommonSimpleSchedulerImpInterfaceTaskSchedulingPool
from GridMapImpInterfaceDataSource import GridMapImpInterfaceDataSource
from BusTrajectoryImpInterfaceDataSource import BusTrajectoryImpInterfaceDataSource
from CommonPrivilege import CommonPrivilege

instanceTrigger = CommonTriggerImpInterfaceTrigger()
instanceSimpleScheduler = CommonSimpleSchedulerImpInterfaceTaskSchedulingPool()

latitude = -0.01
longitude = -0.01
# simu value
globalDictParameter = {}
globalDictParameter['latitude'] = -0.01
globalDictParameter['longitude'] = -0.01
pSubLocation = None


def topic_trajectory_agent_cmd_transaction(msg):
    rospy.logdebug("------------- recv from /trajectory_agent/cmd/transaction-------------- ")
    instanceTrigger.processTopicInfo("/trajectory_agent/cmd/transaction", msg)


def topic_trajectory_agent_cmd_checktrajstate(msg):
    instanceTrigger.processTopicInfo("/trajectory_agent/cmd/checktrajstate", msg)


def topic_chassis_vehicle_state(msg):
    intPilotMode = -1
    try:
        pbStatus = common_system_pilot_mode_pb2.SYSVehicleState()
        pbStatus.ParseFromString(msg.data)
        intPilotMode = pbStatus.pilot_mode
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    instanceTrigger.processPilotUpdate(intPilotMode)


def topic_localization_global(msg):
    global latitude
    global longitude
    global globalDictParameter
    try:
        location = common_localization.Localization()
        location.ParseFromString(msg.data)
        longitude = location.longitude
        latitude = location.latitude
        globalDictParameter['latitude'] = latitude
        globalDictParameter['longitude'] = longitude
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    pSubLocation.unregister()


def addLocalizationListener():
    try:
        strFlagEndFile = "/home/mogo/data/config_end"
        if os.path.exists(strFlagEndFile):
            rospy.Subscriber("/trajectory_agent/cmd/transaction", BinaryData, topic_trajectory_agent_cmd_transaction)
            rospy.Subscriber("/trajectory_agent/cmd/checktrajstate", BinaryData,
                             topic_trajectory_agent_cmd_checktrajstate)
            rospy.Subscriber("/system_master/SysVehicleState", BinaryData, topic_chassis_vehicle_state)
            global pSubLocation
            pSubLocation = rospy.Subscriber('/localization/global', BinaryData, topic_localization_global)
            pass
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def receive_signal(signum, stack):
    instanceSimpleScheduler.RecycleSubProcess()


def init_module():
    global instanceTrigger
    global instanceSimpleScheduler
    try:
        instanceTraj = None
        instanceConfig = ConfigImpInterfaceDataSource()
        instanceHdmapAgent = HdMapAgentImpInterfaceDataSource()
        instanceCommonPrivilege = CommonPrivilege()
        instanceTraj = DfTrajectoryImpInterfaceDataSource()
        instanceAiModle = AiModelImpInterfaceDataSource()
        instanceSlamMap = SlamMapImpInterfaceDataSource()
        instanceGridMap = GridMapImpInterfaceDataSource()


        ## configure
        instanceTrigger.configure()
        instanceConfig.configure()
        instanceHdmapAgent.configure()
        instanceTraj.configure()
        instanceAiModle.configure()
        instanceSlamMap.configure()
        instanceSimpleScheduler.configure()
        instanceGridMap.configure()

        ## init_module
        instanceTrigger.init_module()
        instanceConfig.init_module()
        instanceHdmapAgent.init_module()
        instanceTraj.init_module()
        instanceAiModle.init_module()
        instanceSlamMap.init_module()
        instanceSimpleScheduler.init_module()
        instanceGridMap.init_module()

        # dataSource set Scheduler
        instanceConfig.setScheduler(instanceSimpleScheduler)
        instanceHdmapAgent.setScheduler(instanceSimpleScheduler)
        instanceAiModle.setScheduler(instanceSimpleScheduler)
        instanceSlamMap.setScheduler(instanceSimpleScheduler)
        instanceTraj.setScheduler(instanceSimpleScheduler)
        instanceGridMap.setScheduler(instanceSimpleScheduler)

        # cross
        instanceTrigger.addNotifyDataSourceModule(instanceConfig)
        instanceTrigger.addNotifyDataSourceModule(instanceHdmapAgent)
        instanceTrigger.addNotifyDataSourceModule(instanceAiModle)
        instanceTrigger.addNotifyDataSourceModule(instanceSlamMap)
        instanceTrigger.addNotifyDataSourceModule(instanceTraj)
        instanceTrigger.addNotifyDataSourceModule(instanceGridMap)
        instanceTrigger.addNotifyTaskSchedulerPool(instanceSimpleScheduler)
        signal.signal(signal.SIGCHLD, receive_signal)
        addLocalizationListener()
        instanceTrigger.process_startup(globalDictParameter)
        instanceTrigger.start_loop_internal_timer(globalDictParameter)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def main():
    strCmd = "/bin/rm  -rf /home/mogo/data/update_config_temp"
    os.system(strCmd)
    rospy.init_node('NewUpdateConfig', anonymous=True)
    httpUtils = CommonHttpUtils()
    httpUtils.send_test_dns()
    init_module()


if __name__ == "__main__":
    try:
        main()
        rospy.spin()
    except KeyboardInterrupt as e:
        rospy.loginfo("update_config_simple.py is failed !")
        exit(0)
