#!/usr/bin/env python
# -*- coding: utf-8 -*-
from timeit import Timer

import thread
from threading import Thread,Lock
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
import common.system_pilot_mode_pb2 as common_system_pilot_mode_pb2
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
import collections
import json
from os import path, access, R_OK
import os, sys, stat
import uuid
from std_msgs.msg import String
from roscpp.msg import TopicHz
#import Timer
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



### global area
globalTopicMsgPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalTopicMsgPool')
globalCpuInfoPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalCpuInfoPool')
globalMemInfoPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalMemInfoPool')
globalNodeHealthPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalNodeHealthPool')
globalCollectVehicleInfo = CollectVehicleInfo()

globalCommonPara = CommonPara()
globalPubToTelematicsInfo = rospy.Publisher("/autopilot_info/report_msg_info", BinaryData, queue_size=1000)
globalPubToTelematicsError = rospy.Publisher("/autopilot_info/report_msg_error", BinaryData, queue_size=1000)
globalPubToTelematicsTopicHz = rospy.Publisher("/cloud_debug/report_topic_hz", BinaryData, queue_size=1000)
globalPubToMonitorProcessControlCmd = rospy.Publisher('/monitor_collect/control/status_report/cmd', BinaryData,
                                                      queue_size=1000)
globalPubOperatorToolNodeHealth = rospy.Publisher("/monitor_process/nodes/health/operate_tool", BinaryData,
                                                  queue_size=1000)

tree = lambda: collections.defaultdict(tree)
rDictHzTable = tree()
global_hz_time_write_interval = 0

globalSumCpuMsgRecvInfo = 0
globalListCpuMsgRecvInfo = []

globalSumMemoryMsgRecvInfo = 0
globalListMemoryMsgRecvInfo = []

globalSumNodeHealthRecvInfo = 0
globalListNodeHealthRecvInfo = []
globalDictHostMacInfo = {}
globalDictTableNodeHealth = {}
globalDictTableNodeHealthTimeout = {}
globalDelayTimeInterval = 0

#global_hz_time_write_interval = 0

tree = lambda: collections.defaultdict(tree)
globalDictHzRecord = tree()
globalDictHzFlag  = {}
globalTimeAlignDictHzRecord = tree()
globalTimeAlignDictHzFlag = {}
globalListWaitWriteBuffer  = []
globalHzRecordLock = Lock()
globalHzWarnTime = 0
globalHzHandleTime = 0

def folder_check():
    PATH = '/home/mogo/data/log/filebeat_upload/'
    if os.path.isdir(PATH) and access(PATH, R_OK):
        pass
    else:
        rospy.logwarn("folder not ready,now create path")
        os.makedirs(PATH)

        os.chmod(PATH, 0777)


def task_topic_hz(msg):

    global global_hz_time_write_interval
    global globalDictHzRecord
    global globalDictHzFlag
    global globalListWaitWriteBuffer
    dictHzRecord = tree()
    try:
        rospy.loginfo_throttle(5,"node: %s, topic: %s, type: %d, start: %d, hz: %f, max_delay: %d, stop:%d ",msg.node, msg.topic, msg.type, msg.start, msg.hz, msg.max_delay,msg.stop)
        strType = ""
        if msg.type == 0:
            strType = "pub"

        if msg.type == 1:
            strType = "call"

        ##  process node info write cover
        strConflictKey = "{0}_{1}".format(msg.node,msg.topic)
        rospy.loginfo_throttle(5, "strConflictKey:{0}".format(strConflictKey))
        if  globalDictHzFlag.has_key(strConflictKey) and len(globalDictHzRecord)> 0:
            rospy.loginfo_throttle(5, "same node info  will  cover , first  move to  buffer")
            ###  has node key, need write buffer
            ### fillup  upload time and carinfo
            globalDictHzRecord["log_type"] = "topic_hz"
            globalDictHzRecord['report_stamp'] = (rospy.Time.now().secs * 1000) + (rospy.Time.now().nsecs / 1000000)
            globalDictHzRecord['carinfo']['car_type'] = globalCommonPara.dictCarInfo['car_type']
            globalDictHzRecord['carinfo']['code_version'] = globalCommonPara.dictCarInfo['code_version']
            globalDictHzRecord['carinfo']['car_plate'] = globalCommonPara.dictCarInfo['car_plate']
            ### flush to buffer
            strBufferContent = json.dumps(globalDictHzRecord)
            rospy.logdebug_throttle(5, "+++++++++++++++++++push strBufferContent:{0}".format(strBufferContent))
            ### save buffer to list
            globalListWaitWriteBuffer.append(strBufferContent)
            rospy.logdebug_throttle(5,"------------globalListWaitWriteBuffer size:{0}".format(len(globalListWaitWriteBuffer)))
            ### after write buffer , need  clean flag
            globalDictHzFlag = {}
            rospy.logdebug_throttle(5, "after write buffer , globalDictHzFlag:{0}".format(globalDictHzFlag))
            ### after clean flag , clear globalDictHzRecord
            globalDictHzRecord = tree()
            rospy.logdebug_throttle(5, "after writer buffer, globalDictHzRecord:{0}".format(globalDictHzRecord))

        ## normal  write data
        ### hzFlag add key msg.node
        globalDictHzFlag[strConflictKey] = 0
        globalDictHzRecord[msg.node][msg.topic][strType]['hz']=msg.hz
        globalDictHzRecord[msg.node][msg.topic][strType]['max_delay'] = msg.max_delay
        globalDictHzRecord[msg.node][msg.topic][strType]['stime']= msg.start
        globalDictHzRecord[msg.node][msg.topic][strType]['etime'] = msg.stop
        rospy.logdebug_throttle(5,"=================== after write globalDictHzRecord:{0} ".format(globalDictHzRecord))
        ### message sum
        #global_hz_time_write_interval = global_hz_time_write_interval + 1
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def task_topic_hz_time_align(msg):

    global global_hz_time_write_interval
    global globalListWaitWriteBuffer

    global globalTimeAlignDictHzRecord
    global globalTimeAlignDictHzFlag
    global globalHzWarnTime
    global globalHzHandleTime

    try:
        strType = ""
        if msg.type == 0:
            strType = "pub"

        if msg.type == 1:
            strType = "call"

        ##  process node info write cover
        strConflictKey = "{0}_{1}".format(msg.node,msg.topic)

        if msg.stop > globalHzHandleTime:
            globalHzHandleTime = msg.stop

        if msg.stop < globalHzHandleTime - 10:
            if globalHzWarnTime + 10 < msg.stop:
                rospy.logwarn(" {2} at timestamp {0} will be discarded because it is data {1} seconds ago".format(msg.stop, globalHzHandleTime - msg.stop, strConflictKey))
                globalHzWarnTime = msg.stop
            return

        if not globalTimeAlignDictHzFlag.has_key(msg.stop):
            globalHzRecordLock.acquire()
            globalTimeAlignDictHzFlag[msg.stop] = dict()
            ### fillup  upload time and carinfo
            globalTimeAlignDictHzRecord[msg.stop]["log_type"] = "topic_hz"
            globalTimeAlignDictHzRecord[msg.stop]["etime"] = msg.stop
            globalTimeAlignDictHzRecord[msg.stop]["timestamp"] = msg.stop * 1000
            globalTimeAlignDictHzRecord[msg.stop]['carinfo']['car_type'] = globalCommonPara.dictCarInfo['car_type']
            globalTimeAlignDictHzRecord[msg.stop]['carinfo']['code_version'] = globalCommonPara.dictCarInfo['code_version']
            globalTimeAlignDictHzRecord[msg.stop]['carinfo']['car_plate'] = globalCommonPara.dictCarInfo['car_plate']
            globalHzRecordLock.release()

        if  globalTimeAlignDictHzFlag[msg.stop].has_key(strConflictKey):
            rospy.loginfo_throttle(10,"{0} has received more than 1 msg at time_stamp {1}".format(strConflictKey, msg.stop))
            return

        ## normal  write data
        ### hzFlag add key msg.node
        globalHzRecordLock.acquire()
        globalTimeAlignDictHzFlag[msg.stop][strConflictKey] = 0
        globalTimeAlignDictHzRecord[msg.stop][msg.node][msg.topic][strType]['hz']=msg.hz
        globalTimeAlignDictHzRecord[msg.stop][msg.node][msg.topic][strType]['max_delay'] = msg.max_delay
        globalTimeAlignDictHzRecord[msg.stop][msg.node][msg.topic][strType]['stime']= msg.start
        globalHzRecordLock.release()
        ### message sum
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def task_topic_msg(msg):
    tree = lambda: collections.defaultdict(tree)
    dictMsgInfoRecord = tree()
    try:
        pbRecvMsg = comon_mogo_report_msg_pb2.MogoReportMessage()
        pbRecvMsg.ParseFromString(msg.data)
        pbSend = common_monitor_msg_pb2.MonitorMsg()
        pbSend.reportmsg.timestamp.sec = pbRecvMsg.timestamp.sec

        dictMsgInfoRecord['reportmsg']['timestamp']['sec'] = pbRecvMsg.timestamp.sec

        pbSend.reportmsg.timestamp.nsec = pbRecvMsg.timestamp.nsec

        dictMsgInfoRecord['reportmsg']['timestamp']['nsec'] = pbRecvMsg.timestamp.nsec
        dictMsgInfoRecord['reportmsg']['timestamp'][
            'msec'] = (pbRecvMsg.timestamp.sec * 1000) + (pbRecvMsg.timestamp.nsec / 1000000)
        pbSend.reportmsg.src = pbRecvMsg.src
        rospy.logdebug("pbRecvMsg.src:%s" % (pbRecvMsg.src))
        dictMsgInfoRecord['reportmsg']['src'] = pbRecvMsg.src
        pbSend.reportmsg.level = pbRecvMsg.level
        rospy.logdebug("pbRecvMsg.level%s" % (pbRecvMsg.level))
        dictMsgInfoRecord['reportmsg']['level'] = pbRecvMsg.level
        pbSend.reportmsg.msg = pbRecvMsg.msg

        dictMsgInfoRecord['reportmsg']['msg'] = pbRecvMsg.msg
        pbSend.reportmsg.code = pbRecvMsg.code
        rospy.logdebug("pbRecvMsg.code:%s" % (pbRecvMsg.code))
        dictMsgInfoRecord['reportmsg']['code'] = pbRecvMsg.code
        listTempResult = []
        listTempAction = []
        for elemResult in pbRecvMsg.result:
            listTempResult.append(elemResult)
            rospy.logdebug_throttle(1,"elemResult:%s" % (elemResult))
            pbSend.reportmsg.result.append(str(elemResult))
        for elemAction in pbRecvMsg.actions:
            listTempAction.append(elemAction)
            rospy.logdebug_throttle(1, "elemAction:%s" % (elemAction))
            pbSend.reportmsg.actions.append(str(elemAction))
        dictMsgInfoRecord['reportmsg']['result'] = listTempResult
        dictMsgInfoRecord['reportmsg']['actions'] = listTempAction



        pbSend.carinfo.car_plate = globalCommonPara.dictCarInfo["car_plate"]
        dictMsgInfoRecord['carinfo']['car_plate'] = globalCommonPara.dictCarInfo["car_plate"]
        pbSend.carinfo.car_type = globalCommonPara.dictCarInfo["car_type"]
        dictMsgInfoRecord['carinfo']['car_type'] = globalCommonPara.dictCarInfo["car_type"]
        pbSend.carinfo.code_version = globalCommonPara.dictCarInfo["code_version"]
        dictMsgInfoRecord['carinfo']['code_version'] = globalCommonPara.dictCarInfo["code_version"]
        while True:
            if pbSend.reportmsg.level == "info":
                dictMsgInfoRecord['log_type'] = "msg_record"
                break
            if pbSend.reportmsg.level == "error":
                dictMsgInfoRecord['log_type'] = "msg_record"
                break
            break
        rospy.logdebug_throttle(1, "code_version:%s" % (pbSend.carinfo.code_version))

        strBuffer = pbSend.SerializeToString()
        rosMessage = BinaryData()
        rosMessage.data = strBuffer
        rosMessage.size = len(strBuffer)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    strJson = json.dumps(dictMsgInfoRecord)
    ## send telematics
    # /autopilot_info/report_msg_error
    # /autopilot_info/report_msg_info
    ## Write dest file
    try:
        folder_check()
        while True:
            if pbSend.reportmsg.level == "info":
                with open('/home/mogo/data/log/filebeat_upload/msg_record.log', 'ab+') as f:
                    f.write(strJson)
                    f.write('\n')

                break
            if pbSend.reportmsg.level == "error":
                with open('/home/mogo/data/log/filebeat_upload/msg_record.log', 'ab+') as f:
                    f.write(strJson)
                    f.write('\n')

                break
            break
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))




def topicHzRecvCallback(msg):
    task_topic_hz_time_align(msg)





def topicMsgCallback(msg):
    rospy.loginfo_throttle(2, "recv from channel /autopilot_info/report_msg_info or /topilot_info/report_msg_error ")
    if msg.size > 0:
        globalTopicMsgPool.submit(task_topic_msg, msg)


def task_cpu_info(msg):
    global globalSumCpuMsgRecvInfo
    global globalListCpuMsgRecvInfo
    tree = lambda: collections.defaultdict(tree)
    dictSaveToFile = tree()
    dictTempInfo = json.loads(str(msg.data))
    dictSaveToFile["log_type"] = "cpu_info"
    dictSaveToFile["carinfo"] = globalCommonPara.dictCarInfo
    dictSaveToFile["timestamp"]["sec"] = rospy.Time.now().secs
    dictSaveToFile["timestamp"]["nsec"] = rospy.Time.now().nsecs
    dictSaveToFile["timestamp"]["msec"] = (dictSaveToFile["timestamp"]["sec"] * 1000) + (dictSaveToFile["timestamp"][
                                                                                             "nsec"] / 1000000)
    dictSaveToFile["report_msg"] = dictTempInfo
    dictSaveToFile["report_msg"]["header"]["pilot_mode"] = globalCollectVehicleInfo.int_pilot_mode
    strJsonSaveToFile = json.dumps(dictSaveToFile)
    try:
        folder_check()
        with open('/home/mogo/data/log/filebeat_upload/cpu_info.log', 'a+') as f:
            f.write(strJsonSaveToFile)
            f.write("\n")
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))




def topicCpuStatusCallback(msg):
    rospy.logdebug_throttle(1, "recv from channel /monitor_process/sysinfo/cpu/status ")
    if msg.size > 0:
        globalCpuInfoPool.submit(task_cpu_info, msg)


def task_node_health(msg):
    global globalSumNodeHealthRecvInfo
    global globalListNodeHealthRecvInfo
    global globalDictHostMacInfo
    global globalDictTableNodeHealth
    global globalDictTableNodeHealthTimeout
    tree = lambda: collections.defaultdict(tree)
    dictSaveToFile = tree()
    dictTempInfo = json.loads(str(msg.data))
    strMac = dictTempInfo['header']['mac']
    strIp = dictTempInfo['header']['ip']
    globalDictHostMacInfo[strMac] = 1
    rospy.logdebug_throttle(10,"recv node status from mac:{0},ip: {1}".format(strMac, strIp))




    dictSaveToFile["timestamp"]["sec"] = rospy.Time.now().secs
    if len(dictTempInfo['data']) > 0:
        for key, value in dictTempInfo['data'].items():
            globalDictTableNodeHealth[key] = value
            globalDictTableNodeHealthTimeout[key] = dictSaveToFile["timestamp"]["sec"]

    dictSaveToFile["log_type"] = "node_health"
    dictSaveToFile["carinfo"] = globalCommonPara.dictCarInfo

    dictSaveToFile["timestamp"]["nsec"] = rospy.Time.now().nsecs
    dictSaveToFile["timestamp"]["msec"] = (dictSaveToFile["timestamp"]["sec"] * 1000) + (dictSaveToFile["timestamp"][
                                                                                             "nsec"] / 1000000)
    dictSaveToFile["report_msg"]['data'] = globalDictTableNodeHealth
    dictSaveToFile["report_msg"]["header"]["pilot_mode"] = globalCollectVehicleInfo.int_pilot_mode
    strJsonSaveToFile = json.dumps(dictSaveToFile)
    rosSendMsg = BinaryData()
    rosSendMsg.data = strJsonSaveToFile
    rosSendMsg.size = len(rosSendMsg.data)
    rospy.logdebug_throttle(1,"strJsonSaveToFile: %s" % strJsonSaveToFile)
    try:
        folder_check()
        with open('/home/mogo/data/log/filebeat_upload/node_health.log', 'a+') as f:
            f.write(strJsonSaveToFile)
            f.write("\n")
            globalPubOperatorToolNodeHealth.publish(rosSendMsg)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        #exit(-1)
    pass


def topicNodeStatusCallback(msg):
    rospy.logdebug_throttle(1, "recv from channel /monitor_process/sysinfo/nodes/status")
    if msg.size > 0:
        globalNodeHealthPool.submit(task_node_health, msg)


def task_memory_info(msg):
    global globalSumMemoryMsgRecvInfo
    global globalListMemoryMsgRecvInfo
    tree = lambda: collections.defaultdict(tree)
    dictSaveToFile = tree()
    dictTempInfo = json.loads(str(msg.data))
    dictSaveToFile["log_type"] = "memory_info"
    dictSaveToFile["carinfo"] = globalCommonPara.dictCarInfo
    dictSaveToFile["timestamp"]["sec"] = rospy.Time.now().secs
    dictSaveToFile["timestamp"]["nsec"] = rospy.Time.now().nsecs
    dictSaveToFile["timestamp"]["msec"] = (dictSaveToFile["timestamp"]["sec"] * 1000) + (dictSaveToFile["timestamp"][
                                                                                             "nsec"] / 1000000)
    dictSaveToFile["report_msg"] = dictTempInfo
    dictSaveToFile["report_msg"]["header"]["pilot_mode"] = globalCollectVehicleInfo.int_pilot_mode
    strJsonSaveToFile = json.dumps(dictSaveToFile)
    try:
        folder_check()
        with open('/home/mogo/data/log/filebeat_upload/memory_info.log', 'a+') as f:
            f.write(strJsonSaveToFile)
            f.write("\n")
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        #exit(-1)
    pass


def topicMemoryStatusCallback(msg):
    rospy.logdebug_throttle(1,"recv from channel /monitor_process/sysinfo/memory/status")
    if msg.size > 0:
        globalMemInfoPool.submit(task_memory_info, msg)


def autopilotModeCallback(msg):

    pbStatus = common_vehicle_state_pb2.VehicleState()
    pbStatus.ParseFromString(msg.data)



    global globalCollectVehicleInfo
    globalCollectVehicleInfo = CollectVehicleInfo()
    (globalCollectVehicleInfo.int_pilot_mode) = pbStatus.pilot_mode
    (globalCollectVehicleInfo.b_steer_inference) = pbStatus.steer_inference
    (globalCollectVehicleInfo.b_brake_inference) = pbStatus.brake_inference
    (globalCollectVehicleInfo.b_accel_inference) = pbStatus.accel_inference
    globalCollectVehicleInfo.b_gear_switch_inference = pbStatus.gear_switch_inference
    globalCollectVehicleInfo.b_location_missing = pbStatus.location_missing
    globalCollectVehicleInfo.b_trajectory_missing = pbStatus.trajectory_missing
    globalCollectVehicleInfo.b_chassis_status_missing = pbStatus.chassis_status_missing

    # 1、steer_inference
    # 方向盘干预
    # 2、brake_inference
    # 制动踏板（刹车）干预
    # 3、accel_inference
    # 加速踏板（油门）干预
    # 4、gear_switch_inference
    # 档位切换干预
    # 5、location_missing
    # 定位信息丢失
    # 6、trajectory_missing
    # 轨迹信息丢失
    # 7、lostchassis
    # 车辆底盘丢失（can
    # 节点丢失）

    while True:
        ## MODE_MANUAL
        if globalCollectVehicleInfo.b_steer_inference:
            globalCollectVehicleInfo.int_error_code = 1
            globalCollectVehicleInfo.str_err_msg = "steer_inference"
            break
        if globalCollectVehicleInfo.b_brake_inference:
            globalCollectVehicleInfo.int_error_code = 2
            globalCollectVehicleInfo.str_err_msg = "brake_inference"
            break
        if globalCollectVehicleInfo.b_accel_inference:
            globalCollectVehicleInfo.int_error_code = 3
            globalCollectVehicleInfo.str_err_msg = "accel_inference"
            break
        if globalCollectVehicleInfo.b_gear_switch_inference:
            globalCollectVehicleInfo.int_error_code = 4
            globalCollectVehicleInfo.str_err_msg = "gear_switch_inference"
            break
        if globalCollectVehicleInfo.b_location_missing:
            globalCollectVehicleInfo.int_error_code = 5
            globalCollectVehicleInfo.str_err_msg = "location_missing"
            break
        if globalCollectVehicleInfo.b_trajectory_missing:
            globalCollectVehicleInfo.int_error_code = 6
            globalCollectVehicleInfo.str_err_msg = "trajectory_missing"
            break
        if globalCollectVehicleInfo.b_chassis_status_missing:
            globalCollectVehicleInfo.int_error_code = 7
            globalCollectVehicleInfo.str_err_msg = "lostchassis"
            break
        break


def newAutopilotModeCallback(msg):

    pbStatus = common_system_pilot_mode_pb2.SYSVehicleState()
    pbStatus.ParseFromString(msg.data)

    global globalCollectVehicleInfo
    globalCollectVehicleInfo.int_pilot_mode = pbStatus.pilot_mode


def addLocalizationListener():
    rospy.Subscriber("/autopilot_info/topic_hz", TopicHz, topicHzRecvCallback, queue_size = 10)
    rospy.Subscriber("/autopilot_info/report_msg_info", BinaryData, topicMsgCallback)
    rospy.Subscriber("/autopilot_info/report_msg_error", BinaryData, topicMsgCallback)
    rospy.Subscriber("/monitor_process/sysinfo/cpu/status", BinaryData, topicCpuStatusCallback)
    rospy.Subscriber("/monitor_process/sysinfo/memory/status", BinaryData, topicMemoryStatusCallback)
    rospy.Subscriber("/monitor_process/sysinfo/nodes/status", BinaryData, topicNodeStatusCallback)
    rospy.Subscriber('/system_master/SysVehicleState', BinaryData, newAutopilotModeCallback)




def threadTimeoutRestNodeStatus(strThreadName, intDelay):
    while True:
        intCurrentSec = rospy.Time.now().secs
        global globalDictTableNodeHealthTimeout
        global globalDictTableNodeHealth
        for key, value in globalDictTableNodeHealthTimeout.items():
            if (intCurrentSec - value) > intDelay:
                globalDictTableNodeHealth[key] = "off"
                rospy.logwarn_throttle(2,"node has timeout: " + key)
        time.sleep(intDelay)


def startThreadControlCmd(intTimeVal):
    try:
        thread.start_new_thread(threadTimeoutRestNodeStatus, ("ControlCmd", int(intTimeVal),))
    except:
        rospy.logwarn("Error: unable to start thread")

def flushTopicHzWriterBuffer():
    global globalListWaitWriteBuffer
    try:
        folder_check()
        with open('/home/mogo/data/log/filebeat_upload/topic_hz_log.log', 'ab+') as f:
            if len(globalListWaitWriteBuffer) > 0:
                for line in globalListWaitWriteBuffer:
                    f.write(line)
                    f.write('\n')
            rospy.logdebug_throttle(2, "================================flushTopicHzWriterBuffer write  local disk finished ")
            globalListWaitWriteBuffer = []
            rospy.logdebug_throttle(2, "flushTopicHzWriterBuffer: after flush to  file , globalListWaitWriteBuffer :{0}".format(globalListWaitWriteBuffer))
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def newFlushTopicHzWriterBuffer():
    global globalTimeAlignDictHzRecord
    global globalTimeAlignDictHzFlag
    global globalHzHandleTime
    try:
        folder_check()
        with open('/home/mogo/data/log/filebeat_upload/new_topic_hz_log.log', 'ab+') as f:
            globalHzRecordLock.acquire()
            timestamps = list(globalTimeAlignDictHzRecord.keys())
            timestamps.sort()
            for timestamp in timestamps:
                if timestamp > globalHzHandleTime - 15:
                    break
                globalTimeAlignDictHzFlag.pop(timestamp)
                strBufferContent = json.dumps(globalTimeAlignDictHzRecord.pop(timestamp))
                f.write(strBufferContent)
                f.write('\n')
            globalHzRecordLock.release()

    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def threadFlushTopicHz(intTimeVal):
    while True:
        newFlushTopicHzWriterBuffer()
        time.sleep(30)


def threadCheckHz(intTimeVal):
    while True:
        time.sleep(intTimeVal)
        recent_time = rospy.rostime.Time.now().secs
        if (recent_time - 60) in globalTimeAlignDictHzRecord:
            rospy.loginfo("writing hz file went wrong, didn't write in 30s")
        if (recent_time - 2) not in globalTimeAlignDictHzRecord:
            rospy.loginfo("collecting hz data went wrong, didn't collect in 2s")


def startThreadFlushWaitWriteBufferCmd(intTimeVal):
    try:
        thread.start_new_thread(threadFlushTopicHz, (int(intTimeVal),))
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def startThreadCheckHzWorkingStatus(intTimeVal):
    try:
        thread.start_new_thread(threadCheckHz, (int(intTimeVal),))
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

def main():
    # initial node
    globalCommonPara.initPara()
    rospy.init_node('monitor_collect', anonymous=True)

    global globalDelayTimeInterval
    globalDelayTimeInterval = 10

    # add listener
    folder_check()
    addLocalizationListener()
    startThreadControlCmd(globalDelayTimeInterval)
    startThreadFlushWaitWriteBufferCmd(30)
    startThreadCheckHzWorkingStatus(600)
    ## wait msg
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        rospy.logwarn("monitor.py is failed !")
        exit(0)
