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


def getHostName():
    strCmd = "ifconfig  %s   | grep inet |  grep netmask | awk '{print $2}'" % globalNetCardName
    (status, output) = commands.getstatusoutput(strCmd)
    print "status:%d,output:%s" % (status, output)
    strIp = output

    strCmd2 = "cat /etc/hosts |  grep '%s' | awk '{print $2}'" % (strIp)
    (status, output) = commands.getstatusoutput(strCmd2)
    strHostName = output
    print "status:%d,output:%s" % (status, strHostName)
    return strHostName


def getPkgByFileName(strLaunchFileName):
    strPkgName = ""
    strCmd = "xmllint --xpath \"//@pkg\" %s   | awk -F \"=\" '{print $2}'   2>/dev/null | sed 's/\"//g'" % (
        strLaunchFileName)
    (status, strCmdOutput) = commands.getstatusoutput(strCmd)
    while True:
        if status != 0:
            break
        if status == 0:
            strPkgName = strCmdOutput
            break
        break
    return strPkgName


def getNodeNameByFileName(strLaunchFileName):
    strNodeName = ""
    strCmdOutput1 = ""
    status1 = 0
    strCmdOutput2 = ""
    status2 = 0

    strCmd1 = " xmllint  --xpath '/launch/group/node/@name'  %s  |  awk -F \"=\" '{print $2}'  2>/dev/null" % (
        strLaunchFileName)
    (status1, strCmdOutput1) = commands.getstatusoutput(strCmd1)
    print "strCmd1:%s , status1:%d, strCmdOutput1:%s" % (strCmd1, status1, strCmdOutput1)

    strCmd2 = " xmllint  --xpath '/launch/node/@name'  %s  |  awk -F \"=\" '{print $2}'  2>/dev/null " % (
        strLaunchFileName)
    (status2, strCmdOutput2) = commands.getstatusoutput(strCmd2)
    print "strCmd2:%s, status1:%d, strCmdOutput2:%s" % (strCmd2, status2, strCmdOutput2)
    while True:
        if (status1 == 0) and (len(strCmdOutput1) > 0) and (strCmdOutput1.find("XPath") < 0):
            strNodeName = strCmdOutput1.strip('"')
            break
        if (status2 == 0) and (len(strCmdOutput2) > 0) and (strCmdOutput2.find("XPath") < 0):
            strNodeName = strCmdOutput2.strip('"')
            break
        break
    print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@     strNodeName:%s" % (strNodeName)
    return strNodeName


def readNodeList():
    strHostName = getHostName()

    strFileListName = "/autocar-code/install/share/launch/%s.list" % (strHostName)
    print "strFileListName:%s" % (strFileListName)

    if os.path.exists(strFileListName):
        pass
    else:
        print "file :%s not exists ,checkt host name and net_card_name" % (strFileListName)
        sys.exit(-1)
    linesLaunchFile_1 = []
    with open(strFileListName, 'r') as f:
        listResult = (f.readlines())
        for idx in range(len(listResult)):
            linesLaunchFile_1.append(listResult[idx].strip('\n'))
    print "start---------------------listResult"
    print  linesLaunchFile_1
    print "end---------------------listResult"

    ## search launch file
    linesLaunchFile_2 = []
    linesNodeName = []
    for idx in range(len(linesLaunchFile_1)):
        print "start process : %s " % (linesLaunchFile_1[idx])
        strCmdRoslanchSearch = "roslaunch --files  %s   2>/dev/null" % (linesLaunchFile_1[idx])
        (status, include_files) = commands.getstatusoutput(strCmdRoslanchSearch)
        print "start ---------------------include_files"
        print include_files
        print "end -----------------------include_files"
        if status != 0:
            print "status !=  0  ignore current , continue"
            continue
        else:
            print "status == 0  normal process "
            listIncludeFiles = include_files.split('\n', -1)
            print listIncludeFiles
            pass

        for idx_child_file in range(len(listIncludeFiles)):
            if len(listIncludeFiles[idx_child_file]) == 0:
                continue
            print "process include_files[idx_child_file]:%s" % listIncludeFiles[idx_child_file]
            pkgName = getPkgByFileName(listIncludeFiles[idx_child_file])
            if len(pkgName) == 0:
                print "get file %s len(pkgName) == 0  now continue" % (listIncludeFiles[idx_child_file])
                continue
            strNodeName = getNodeNameByFileName(listIncludeFiles[idx_child_file])
            if len(strNodeName) == 0:
                print "len(strNodeName) == 0 %s" % strNodeName
            if len(strNodeName.strip()) > 0:
                linesLaunchFile_2.append(listIncludeFiles[idx_child_file])
                print "##############################################now update  list  strNodeName:%s ,len1:%d,len2:%d " % (
                    strNodeName.strip(), len(strNodeName.strip()), len(strNodeName))
                linesNodeName.append(strNodeName)
    print "start______________linesNodeName"
    print  linesNodeName
    print "end----------------linesNodeName"
    return linesNodeName


def node_status_check(listNodeList, strUuid):
    ps_num = 0
    tree = lambda: collections.defaultdict(tree)
    node_state_dict = tree()
    ping_flag = False
    node_alive_li = []
    prog = Popen("rosnode ping -a", shell=True, stdout=PIPE)
    node_li = prog.stdout.read()
    # output = prog.communicate()
    # output_li = list(output)
    node_li = node_li.split("\n")
    for ping_line in node_li:
        ping_li = ping_line.split(" ")
        if ping_li[0] == "pinging":
            if ping_flag and len(node_alive_li) > 0:
                node_alive_li.pop()
            ping_flag = True
            node_alive_li.append(ping_li[1])
        else:
            ping_flag = False
    print(node_alive_li)

    for node_name in listNodeList:
        if node_name in node_alive_li:
            rospy.loginfo(node_name + " on")
            node_state_dict['data'][node_name] = "on"
            ps_num += 1
        else:
            # rospy.logerr(node_name + " is off, trying to restart...")
            rospy.logerr(node_name + " is off")
            node_state_dict['data'][node_name] = "off"
            node_state_dict['header']['timestamp']['sec'] = rospy.Time.now().secs
            node_state_dict['header']['timestamp']['nsec'] = rospy.Time.now().nsecs
            # node_state_dict['header']['uuid'] = strUuid
            node_state_dict['header']['ip'] = globalDictIpInfo['ip']
            node_state_dict['header']['mac'] = globalDictIpInfo['mac']
    nodemsg = json.dumps(node_state_dict)
    print "node_health_status:%s" % (nodemsg)
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
        dictMemOut['header']['timestamp']['sec'] = rospy.Time.now().secs
        dictMemOut['header']['timestamp']['nsec'] = rospy.Time.now().nsecs
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
    dictCpuInfo['header']['timestamp']['sec'] = rospy.Time.now().secs
    dictCpuInfo['header']['timestamp']['nsec'] = rospy.Time.now().nsecs
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


def controlStatusCmdRecvCallBack(msg):
    if msg.size > 0:
        strCmdContent = str(msg.data)
        while True:
            if 1:
                globalTaskExecutePool.submit(mem_watch, strCmdContent)
                globalTaskExecutePool.submit(cpu_watch, strCmdContent)
                globalTaskExecutePool.submit(node_watch, strCmdContent)
                break
            break


def addLocalizationListener():
    rospy.Subscriber("/monitor_collect/control/status_report/cmd", BinaryData, controlStatusCmdRecvCallBack)


def main():
    # initial node
    globalCommonPara.initPara()
    rospy.init_node('monitor_process', anonymous=True)
    addLocalizationListener()
    # add listener
    global globalNetCardName
    strFullParaName = "%s/net_card_name" % (rospy.get_name())
    print "strFullParaName:%s" % strFullParaName
    temp = rospy.get_param(strFullParaName)
    if len(temp) == 0:
        globalNetCardName = "ens33"
    else:
        globalNetCardName = temp
    #global globalDictIpInfo
    tempNetToos = NetTools()
    global globalDictIpInfo
    globalDictIpInfo = tempNetToos.envInit(globalNetCardName)
    global globalListNode
    globalListNode = readNodeList()
    print "=============================set globalCollectInterval:%d" % (globalCollectInterval)
    print globalListNode
    # node_watch("")
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
