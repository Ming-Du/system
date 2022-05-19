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
    XiverType = 0
    strHostName = ""
    try:
        strCmdCheckMultiXiver = "cat  /etc/hosts | grep slave | wc -l"
        (status, output) = commands.getstatusoutput(strCmdCheckMultiXiver)
        if status == 0:
            print "output:{0}".format(output)
            while True:
                if int(output) == 1:
                    XiverType = 2
                    break

                if int(output) == 0:
                    XiverType = 1
                    break

                if int(output) > 1:
                    XiverType = 6
                    break
                break

        strCmd = "ifconfig  %s   | grep inet |  grep netmask | awk '{print $2}'" % globalNetCardName
        (status, output) = commands.getstatusoutput(strCmd)
        print "status:%d,output:%s" % (status, output)
        strIp = output

        strCmd2 = "cat /etc/hosts |  grep '%s' | awk '{print $2}'" % (strIp)
        (status, output) = commands.getstatusoutput(strCmd2)
        if output == "rosmaster":
            while True:
                if XiverType == 2:
                    strHostName = "rosmaster"
                    break

                if XiverType == 1:
                    strHostName = "all"
                    break

                if XiverType == 6:
                    strHostName = "rosmaster-102"
                    break
                break
        else:
            strHostName = output
        print "status:%d,output:%s" % (status, strHostName)
    except Exception as e:
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():';
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    return strHostName


def readNodeList():
    listAllNode = []
    linesLaunchFile = []
    try:
        strHostName = getHostName()
        strFileListName = "/autocar-code/install/share/launch/%s.list" % (strHostName)
        # print "strFileListName:%s" % (strFileListName)
        # strFileListName = "/home/mogo/data/jhf/system/launch/all.list"

        if os.path.exists(strFileListName):
            pass
        else:
            print "file :%s not exists ,checkt host name and net_card_name" % (strFileListName)
            sys.exit(-1)

        with open(strFileListName, 'r') as f:
            contents = f.read()
            lines = contents.split('\n')
            print "lines:{0}".format(lines)
            for idx in range(len(lines)):
                if len(lines[idx]) > 0:
                    linesLaunchFile.append(lines[idx])
        # linesLaunchFile.append("/home/mogo/data/radar_408_front_308_rear.launch")
        for idx in range(len(linesLaunchFile)):
            strCmd = "roslaunch --nodes {0}".format(linesLaunchFile[idx])
            print  "strCmd :{0}".format(strCmd)
            (status, output) = commands.getstatusoutput(strCmd)
            if status == 0:
                multy_list = output.split('\n')
                print "multy_list: {0}".format(multy_list)
                for input_idx in range(len(multy_list)):
                    if len(multy_list[input_idx]) > 0:
                        listAllNode.append(multy_list[input_idx])
    except Exception as e:
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():'
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    print "start______________linesNodeName"
    print listAllNode
    print "end----------------linesNodeName"
    return listAllNode


def node_status_check(listNodeList, strUuid):
    try:
        print "==========enter node_status_check"
        tree = lambda: collections.defaultdict(tree)
        print "22"
        node_state_dict = tree()
        print "44"
        pinged = []
        unpinged = []
        verbose = False
        skip_cache = False
        print "33"
        print "11"
        print "listNodeList:{0}".format(listNodeList)
        for node in listNodeList:
            if rosnode.rosnode_ping(node, max_count=1, verbose=verbose, skip_cache=skip_cache):
                pinged.append(node)
            else:
                unpinged.append(node)
        print "=========================pinged:{0}".format(pinged)
        print "==========================unpinged:{0}".format(unpinged)

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
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():'
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    print "=================================current node_health_status:%s" % nodemsg
    if len(nodemsg) > 0:
        rosSendMsg = BinaryData()
        rosSendMsg.size = len(nodemsg)
        rosSendMsg.data = nodemsg
        pub_node.publish(rosSendMsg)
        print "send node health success"


def node_watch(strUuid):
    node_status_check(globalListNode, strUuid)


def mem_watch(strUuid):
    (status, memory_out) = commands.getstatusoutput("cat /proc/meminfo")
    print status
    # print type(memory_out)
    # print memory_out
    listFormatMemory = memory_out.split('\n', -1)
    # print listFormatMemory
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
        #dictMemOut['header']['timestamp']['msec']=int(dictMemOut['header']['timestamp']['sec'])*1000 + int(dictMemOut['header']['timestamp']['nsec'])/1000000
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
        print strMemOut
        if len(strMemOut) > 0:
            rosSendMsg = BinaryData()
            rosSendMsg.size = len(strMemOut)
            rosSendMsg.data = strMemOut
            pub_memory.publish(rosSendMsg)
            print "send memory info success"


def cpu_watch(strUuid):
    # get cpunum
    # cat / proc / cpuinfo | grep  processor | wc - l
    (status, cpuInfoOut) = commands.getstatusoutput("top -bn1  |  head -n  5  |  grep Cpu |  awk -F[,] '{print $4}'  "

                                                    "| awk  -F   ' ' '{print $1}'")
    floatUsedCpu = 0.0
    while True:
        if status == 0:
            print cpuInfoOut
            floatIdleCpu = float(cpuInfoOut)
            floatUsedCpu = 100.0 - floatIdleCpu
            break
        if status != 0:
            print "get cpu used error"
            break
        break
    print "floatUsedCpu:%f" % floatUsedCpu
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
    print strCpuInfo
    if len(strCpuInfo) > 0:
        rosSendMsg = BinaryData()
        rosSendMsg.size = len(strCpuInfo)
        rosSendMsg.data = strCpuInfo
        pub_cpu.publish(rosSendMsg)
        print "send cpu_status success"


def ControlStatusCmdReportCallBack():
    while True:
        strCmdContent = str(uuid.uuid1())
        globalTaskExecutePool.submit(mem_watch, strCmdContent)
        globalTaskExecutePool.submit(cpu_watch, strCmdContent)
        globalTaskExecutePool.submit(node_watch, strCmdContent)
        time.sleep(5)


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
    print "strFullParaName:%s" % strFullParaName
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
    print "=============================set globalCollectInterval:%d" % (globalCollectInterval)
    print globalListNode

    sys_report_thread = SysInfoWatchThread()
    sys_report_thread.start()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
