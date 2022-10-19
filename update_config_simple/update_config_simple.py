#!/usr/bin/env python
# -*- coding: utf-8 -*-
import commands
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


times = 0
strFlagFile = "/home/mogo/autopilot/share/update_config_simple/ready.flag"
if os.path.exists(strFlagFile):
    os.remove(strFlagFile)
while True:
    times = times + 1
    strFlagFile = "/home/mogo/autopilot/share/update_config_simple/ready.flag"
    if os.path.exists(strFlagFile):
        break
    if not os.path.exists(strFlagFile):
        strCmd = "sudo apt-get update  &&  sudo apt-get  install -y python-requests  && sudo apt-get install -y python-schedule && sudo apt-get install  python-pycurl "
        status, output = commands.getstatusoutput(strCmd)

        if status == 0:
            strTouchCmd = "touch  {0}".format(strFlagFile)
            strDirName = os.path.dirname(strFlagFile)
            if not os.path.exists(strDirName):
                os.makedirs(strDirName)
            os.system(strTouchCmd)
            if os.path.exists(strFlagFile):
                break

    time.sleep(5)

from autopilot_msgs.msg import BinaryData
import proto.localization_pb2 as common_localization
import proto.vehicle_state_pb2 as common_vehicle_state_pb2
from entity.LocInfo import LocInfo
from entity.CommonPara import CommonPara
import proto.message_pad_pb2 as common_message_pad
import InterfaceDataSource
from ConfigImpInterfaceDataSource import ConfigImpInterfaceDataSource
from HdMapAgentImpInterfaceDataSource import HdMapAgentImpInterfaceDataSource
from TrajectoryImpInterfaceDataSource import TrajectoryImpInterfaceDataSource
from AiModelImpInterfaceDataSource import AiModelImpInterfaceDataSource
from SlamMapImpInterfaceDataSource import SlamMapImpInterfaceDataSource
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool
from CommonTriggerImpInterfaceTrigger import CommonTriggerImpInterfaceTrigger
from CommonSimpleSchedulerImpInterfaceTaskSchedulingPool import CommonSimpleSchedulerImpInterfaceTaskSchedulingPool


instanceTrigger = CommonTriggerImpInterfaceTrigger()

latitude = -0.01
longitude = -0.01
#simu value
globalDictParameter = {'latitude': 39.916527, 'longitude': 116.397128}

def topic_trajectory_agent_cmd_transaction(msg):
    print "------------- recv from /trajectory_agent/cmd/transaction-------------- "
    instanceTrigger.processTopicInfo("/trajectory_agent/cmd/transaction", msg)


def topic_trajectory_agent_cmd_checktrajstate(msg):
    instanceTrigger.processTopicInfo("/trajectory_agent/cmd/checktrajstate", msg)


def topic_chassis_vehicle_state(msg):
    intPilotMode = -1
    try:
        pbStatus = common_vehicle_state_pb2.VehicleState()
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
    latitude = -0.01
    longitude = -0.01
    globalDictParameter['latitude'] = -0.01
    globalDictParameter['longitude'] = -0.01
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
        rospy.logwarn("longitude:{0},latitude:{1}".format(globalDictParameter['longitude'], globalDictParameter['latitude']))


def addLocalizationListener():
    try:
        rospy.Subscriber("/trajectory_agent/cmd/transaction", BinaryData, topic_trajectory_agent_cmd_transaction)
        rospy.Subscriber("/trajectory_agent/cmd/checktrajstate", BinaryData, topic_trajectory_agent_cmd_checktrajstate)
        rospy.Subscriber("/chassis/vehicle_state", BinaryData, topic_chassis_vehicle_state)
        rospy.Subscriber('/localization/global', BinaryData, topic_localization_global)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))



def init_module():
    global instanceTrigger
    try:
        instanceConfig = ConfigImpInterfaceDataSource()
        instanceHdmapAgent = HdMapAgentImpInterfaceDataSource()
        #instanceTraj = TrajectoryImpInterfaceDataSource()
        instanceAiModle = AiModelImpInterfaceDataSource()
        instanceSlamMap = SlamMapImpInterfaceDataSource()
        instanceScheduler = CommonSchedulerImpInterfaceTaskSchedulingPool()
        instanceSimpleScheduler = CommonSimpleSchedulerImpInterfaceTaskSchedulingPool()

        ## configure
        instanceTrigger.configure()
        instanceConfig.configure()
        instanceHdmapAgent.configure()
        # instanceTraj.configure()
        instanceAiModle.configure()
        instanceSlamMap.configure()
        instanceScheduler.configure()
        instanceSimpleScheduler.configure()

        ## init_module
        instanceTrigger.init_module()
        instanceConfig.init_module()
        instanceHdmapAgent.init_module()
        # instanceTraj.init_module()
        instanceAiModle.init_module()
        instanceSlamMap.init_module()
        instanceScheduler.init_module()
        instanceSimpleScheduler.init_module()

        #dataSource set Scheduler
        instanceConfig.setScheduler(instanceSimpleScheduler)
        instanceHdmapAgent.setScheduler(instanceSimpleScheduler)
        instanceAiModle.setScheduler(instanceSimpleScheduler)
        instanceSlamMap.setScheduler(instanceSimpleScheduler)



        # cross
        instanceTrigger.addNotifyDataSourceModule(instanceConfig)
        # instanceTrigger.addNotifyDataSourceModule(instanceHdmapAgent)
        # instanceTrigger.addNotifyDataSourceModule(instanceAiModle)
        # instanceTrigger.addNotifyDataSourceModule(instanceSlamMap)
        # instanceTrigger.addNotifyTaskSchedulerPool(instanceSimpleScheduler)
        addLocalizationListener()
        instanceTrigger.process_startup(globalDictParameter)
        instanceTrigger.start_loop_internal_timer(globalDictParameter)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def main():
    rospy.init_node('NewUpdateConfig', anonymous=True)
    init_module()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
