#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import traceback
import uuid

from random import random

import rospy
import rosnode
import rosparam
import os
from threading import Thread

import std_msgs
from std_msgs.msg import String
from rospy import init_node, Subscriber, Publisher
import json
# import psutil
import collections
import sys
# import simplejson
import logging
import re
import time
import datetime
import os

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
import commands
from xml.dom.minidom import parse
import xml.dom.minidom

import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Process, Manager
import psutil
import collections
from entity.NetTools import NetTools

# from xml.dom.minidom import parse
# import xml.dom.minidom
import entity.GenLaunchList as commonGenLaunchList

globalTaskExecutePool = ThreadPoolExecutor(max_workers=4, thread_name_prefix='ThreadPoolTaskExecutePool')
globalCollectVehicleInfo = CollectVehicleInfo()
globalCommonPara = CommonPara()

pub_node = rospy.Publisher('/monitor_process/sysinfo/nodes/status', BinaryData, queue_size=1000)
pub_memory = rospy.Publisher('/monitor_process/sysinfo/memory/status', BinaryData, queue_size=1000)
pub_cpu = rospy.Publisher('/monitor_process/sysinfo/cpu/status', BinaryData, queue_size=1000)

globalDictIpInfo = {}
globalCollectInterval = 0
globalListNode = []
globalNetCardName = ""


# set_msg_log_pub_info = None
# set_msg_log_pub_error = None


def getHostName():
    strHostName = ""
    try:
        strCmd = "ifconfig  %s   | grep inet |  grep netmask | awk '{print $2}'" % globalNetCardName
        (status, output) = commands.getstatusoutput(strCmd)
        rospy.logdebug("status:%d,output:%s" % (status, output))
        strIp = output

        strCmd2 = "cat /etc/hosts |  grep '%s' | awk '{print $2}' | head -n 1" % (strIp)
        (status, output) = commands.getstatusoutput(strCmd2)
        if status == 0 and len(output) > 0:
            strHostName = output
        rospy.logdebug("status:%d,output:%s" % (status, strHostName))
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    return strHostName


def readNodeList():
    listAllNode = []
    linesLaunchFile = []
    strFileListName = ""
    try:
        while True:
            strHostName = getHostName()
            if len(strHostName) == 0:
                break
            instanceGenLaunchList = commonGenLaunchList.GenLaunchList()
            instanceGenLaunchList.initData()
            strFileListName, ret, strErrorMsg = instanceGenLaunchList.getLaunchFilePath(strHostName)
            if len(strFileListName) == 0 or ret == -1 or ret == -2:
                break
            break

        #rospy.loginfo("=========== strFileName:{0}, ret:{1},strErrorMsg:{2}".format(strFileListName, ret, strErrorMsg))

        if not os.path.exists(strFileListName):
            rospy.logerr("file :%s not exists ,checkt host name and net_card_name" % (strFileListName))
            sys.exit(-1)

        with open(strFileListName, 'r') as f:
            contents = f.read()
            lines = contents.split('\n')

            for idx in range(len(lines)):
                if len(lines[idx]) > 0:
                    linesLaunchFile.append(lines[idx])
        # linesLaunchFile.append("/home/mogo/data/radar_408_front_308_rear.launch")
        for idx in range(len(linesLaunchFile)):
            strCmd = "roslaunch --nodes {0}".format(linesLaunchFile[idx])
            rospy.logdebug("strCmd :{0}".format(strCmd))
            (status, output) = commands.getstatusoutput(strCmd)
            if status == 0:
                multy_list = output.split('\n')
                rospy.loginfo("multy_list: {0}".format(multy_list))
                for input_idx in range(len(multy_list)):
                    if len(multy_list[input_idx]) > 0:
                        if str(multy_list[input_idx]).__contains__("No handlers could") or str(multy_list[input_idx]).__contains__("redis as param server"):
                            rospy.loginfo("ignore name:{0}".format(multy_list[input_idx]))
                        else:
                            rospy.loginfo("---------------------add node name:{0}".format(multy_list[input_idx]))
                            listAllNode.append(multy_list[input_idx])
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    return listAllNode







def node_status_check(listNodeList, strUuid):
    try:

        tree = lambda: collections.defaultdict(tree)

        node_state_dict = tree()

        pinged = []
        unpinged = []
        verbose = False
        skip_cache = False


        rospy.logdebug("listNodeList:{0}".format(listNodeList))
        for node in listNodeList:
            if rosnode.rosnode_ping(node, max_count=1, verbose=verbose, skip_cache=skip_cache):
                pinged.append(node)
            else:
                unpinged.append(node)
        rospy.logdebug("=========================pinged:{0}".format(pinged))
        rospy.logdebug("==========================unpinged:{0}".format(unpinged))

        for elem_name in pinged:
            rospy.loginfo(elem_name + " on")
            node_state_dict['data'][elem_name] = "on"

        for elem_name in unpinged:
            rospy.logerr(elem_name + " is off")
            node_state_dict['data'][elem_name] = "off"
        # node_state_dict['header']['timestamp']['sec'] = rospy.Time.now().secs
        # node_state_dict['header']['timestamp']['nsec'] = rospy.Time.now().nsecs
        # node_state_dict['header']['timestamp']['msec'] = int(node_state_dict['header']['timestamp']['sec'])*1000 + int(node_state_dict['header']['timestamp']['nsec'])/1000000

        # node_state_dict['header']['uuid'] = strUuid
        node_state_dict['header']['ip'] = globalDictIpInfo['ip']
        node_state_dict['header']['mac'] = globalDictIpInfo['mac']
        nodemsg = json.dumps(node_state_dict)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    if len(nodemsg) > 0:
        rosSendMsg = BinaryData()
        rosSendMsg.size = len(nodemsg)
        rosSendMsg.data = nodemsg
        pub_node.publish(rosSendMsg)
        rospy.logdebug_throttle(1,"send node health success")


def node_watch(strUuid):
    node_status_check(globalListNode, strUuid)


def mem_watch(strUuid):
    (status, memory_out) = commands.getstatusoutput("cat /proc/meminfo")



    listFormatMemory = memory_out.split('\n', -1)

    dictMemInfo = collections.OrderedDict()
    for idx in range(len(listFormatMemory)):
        if len(listFormatMemory[idx]) > 0:
            tempList = listFormatMemory[idx].split(':', 1)
            if len(tempList) == 2:
                dictMemInfo[tempList[0]] = tempList[1].strip()
    if len(dictMemInfo) > 0:
        tree = lambda: collections.defaultdict(tree)
        dictMemOut = tree()
        # dictMemOut['header']['timestamp']['sec'] = rospy.Time.now().secs
        # dictMemOut['header']['timestamp']['nsec'] = rospy.Time.now().nsecs
        # dictMemOut['header']['timestamp']['msec']=int(dictMemOut['header']['timestamp']['sec'])*1000 + int(dictMemOut['header']['timestamp']['nsec'])/1000000
        # dictMemOut['header']['uuid'] = strUuid
        dictMemOut['header']['ip'] = globalDictIpInfo['ip']
        dictMemOut['header']['mac'] = globalDictIpInfo['mac']
        dictMemOut['data']['MemTotal'] = dictMemInfo['MemTotal']
        dictMemOut['data']['MemFree'] = dictMemInfo['MemFree']
        dictMemOut['data']['MemAvailable'] = dictMemInfo['MemAvailable']
        dictMemOut['data']['Buffers'] = dictMemInfo['Buffers']
        dictMemOut['data']['Cached'] = dictMemInfo['Cached']
        dictMemOut['data']['SwapCached'] = dictMemInfo['SwapCached']
        dictMemOut['data']['SwapTotal'] = dictMemInfo['SwapTotal']
        dictMemOut['data']['SwapFree'] = dictMemInfo['SwapFree']

        strMemOut = json.dumps(dictMemOut)
        rospy.logdebug(strMemOut)
        if len(strMemOut) > 0:
            rosSendMsg = BinaryData()
            rosSendMsg.size = len(strMemOut)
            rosSendMsg.data = strMemOut
            pub_memory.publish(rosSendMsg)
            rospy.logdebug_throttle(1,"send memory info success")


def cpu_watch(strUuid):
    # get cpunum
    # cat / proc / cpuinfo | grep  processor | wc - l
    (status, cpuInfoOut) = commands.getstatusoutput("top -bn1  |  head -n  5  |  grep Cpu |  awk -F[,] '{print $4}'  "

                                                    "| awk  -F   ' ' '{print $1}'")
    floatUsedCpu = 0.0
    while True:
        if status == 0:

            floatIdleCpu = float(cpuInfoOut)
            floatUsedCpu = 100.0 - floatIdleCpu
            break
        if status != 0:
            rospy.logwarn("get cpu used error")
            break
        break
    rospy.logdebug(2,"floatUsedCpu:%f" % floatUsedCpu)
    tree = lambda: collections.defaultdict(tree)
    dictCpuInfo = tree()
    # dictCpuInfo['header']['timestamp']['sec'] = rospy.Time.now().secs
    # dictCpuInfo['header']['timestamp']['nsec'] = rospy.Time.now().nsecs
    # dictCpuInfo['header']['timestamp']['msec']=int(dictCpuInfo['header']['timestamp']['sec']) * 1000 + int(dictCpuInfo['header']['timestamp']['nsec'])/1000000
    dictCpuInfo['header']["mac"] = globalDictIpInfo["mac"]
    dictCpuInfo['header']["ip"] = globalDictIpInfo["ip"]
    # dictCpuInfo['header']["uuid"] = strUuid
    dictCpuInfo['data']['used_cpu'] = int(floatUsedCpu)

    strCpuInfo = json.dumps(dictCpuInfo)

    if len(strCpuInfo) > 0:
        rosSendMsg = BinaryData()
        rosSendMsg.size = len(strCpuInfo)
        rosSendMsg.data = strCpuInfo
        pub_cpu.publish(rosSendMsg)
        rospy.logdebug_throttle(1,"send cpu_status success")


def ControlStatusCmdReportCallBack():
    while True:
        strCmdContent = str(uuid.uuid1())
        globalTaskExecutePool.submit(mem_watch, strCmdContent)
        globalTaskExecutePool.submit(cpu_watch, strCmdContent)
        globalTaskExecutePool.submit(node_watch, strCmdContent)
        time.sleep(10)


def addLocalizationListener():
    rospy.Subscriber("/monitor_collect/control/status_report/cmd", BinaryData, controlStatusCmdRecvCallBack)


class SysInfoWatchThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        ControlStatusCmdReportCallBack()


def main():
    # initial node
    globalCommonPara.initPara()
    rospy.init_node('monitor_process', anonymous=True)
    # addLocalizationListener()
    # add listener
    global globalNetCardName
    strFullParaName = "%s/net_card_name" % (rospy.get_name())
    rospy.loginfo("strFullParaName:%s" % strFullParaName)
    temp = rospy.get_param(strFullParaName)
    if len(temp) == 0:
        globalNetCardName = "ens33"
    else:
        globalNetCardName = temp
    # global globalDictIpInfo
    tempNetToos = NetTools()
    global globalDictIpInfo
    globalDictIpInfo = tempNetToos.envInit(globalNetCardName)
    global globalListNode
    globalListNode = readNodeList()
    rospy.logdebug("=============================set globalCollectInterval:%d" % (globalCollectInterval))


    sys_report_thread = SysInfoWatchThread()
    sys_report_thread.start()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        rospy.logwarn("monitor.py is failed !")
        exit(0)
