#!/usr/bin/env python
# -*- coding: utf-8 -*-
from timeit import Timer

import thread
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
globalTopicHzPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalTopicHzPool')
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
listSubScriptHzItem = []
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
globalListWaitWriteBuffer  = []


def folder_check():
    PATH = '/home/mogo/data/log/filebeat_upload/'
    if os.path.isdir(PATH) and access(PATH, R_OK):
        print "folder exists and is readable"
    else:
        print "folder not ready,now create path"
        os.makedirs(PATH)
        print os.path.isdir(PATH)
        os.chmod(PATH, 0777)


def task_topic_hz(msg):
    print "++++++++++++++++++++++++"
    global global_hz_time_write_interval
    global globalDictHzRecord
    global globalDictHzFlag
    global globalListWaitWriteBuffer
    dictHzRecord = tree()
    try:
        #rospy.loginfo("node: %s, topic: %s, type: %d, start: %d, hz: %f, max_delay: %d, stop:%d ",msg.node, msg.topic, msg.type, msg.start, msg.hz, msg.max_delay,msg.stop)
        strType = ""
        if msg.type == 0:
            strType = "pub"

        if msg.type == 1:
            strType = "call"

        ##  process node info write cover
        strConflictKey = "{0}_{1}".format(msg.node,msg.topic)
        print "strConflictKey:{0}".format(strConflictKey)
        if  globalDictHzFlag.has_key(strConflictKey) and len(globalDictHzRecord)> 0:
            print "same node info  will  cover , first  move to  buffer"
            ###  has node key, need write buffer
            ### fillup  upload time and carinfo
            globalDictHzRecord["log_type"] = "topic_hz"
            globalDictHzRecord['report_stamp'] = (rospy.Time.now().secs * 1000) + (rospy.Time.now().nsecs / 1000000)
            globalDictHzRecord['carinfo']['car_type'] = globalCommonPara.dictCarInfo['car_type']
            globalDictHzRecord['carinfo']['code_version'] = globalCommonPara.dictCarInfo['code_version']
            globalDictHzRecord['carinfo']['car_plate'] = globalCommonPara.dictCarInfo['car_plate']
            ### flush to buffer
            strBufferContent = json.dumps(globalDictHzRecord)
            print "+++++++++++++++++++push strBufferContent:{0}".format(strBufferContent)
            ### save buffer to list
            globalListWaitWriteBuffer.append(strBufferContent)
            print "------------globalListWaitWriteBuffer size:{0}".format(len(globalListWaitWriteBuffer))
            ### after write buffer , need  clean flag
            globalDictHzFlag = {}
            print "after write buffer ,  globalDictHzFlag:{0}".format(globalDictHzFlag)
            ### after clean flag , clear globalDictHzRecord
            globalDictHzRecord = tree()
            print "after writer buffer, globalDictHzRecord:{0}".format(globalDictHzRecord)

        ## normal  write data
        ### hzFlag add key msg.node
        globalDictHzFlag[strConflictKey] = 0
        globalDictHzRecord[msg.node][msg.topic][strType]['hz']=msg.hz
        globalDictHzRecord[msg.node][msg.topic][strType]['max_delay'] = msg.max_delay
        globalDictHzRecord[msg.node][msg.topic][strType]['stime']= msg.start
        globalDictHzRecord[msg.node][msg.topic][strType]['etime'] = msg.stop
        print "=================== after write globalDictHzRecord:{0} ".format(globalDictHzRecord)
        ### message sum
        #global_hz_time_write_interval = global_hz_time_write_interval + 1
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



def task_topic_msg(msg):
    tree = lambda: collections.defaultdict(tree)
    dictMsgInfoRecord = tree()
    try:
        pbRecvMsg = comon_mogo_report_msg_pb2.MogoReportMessage()
        pbRecvMsg.ParseFromString(msg.data)
        pbSend = common_monitor_msg_pb2.MonitorMsg()
        pbSend.reportmsg.timestamp.sec = pbRecvMsg.timestamp.sec
        print "timestamp.sec:%d" % (pbRecvMsg.timestamp.sec)
        dictMsgInfoRecord['reportmsg']['timestamp']['sec'] = pbRecvMsg.timestamp.sec

        pbSend.reportmsg.timestamp.nsec = pbRecvMsg.timestamp.nsec
        print "timestamp.nsec:%d" % (pbRecvMsg.timestamp.nsec)
        dictMsgInfoRecord['reportmsg']['timestamp']['nsec'] = pbRecvMsg.timestamp.nsec
        dictMsgInfoRecord['reportmsg']['timestamp'][
            'msec'] = (pbRecvMsg.timestamp.sec * 1000) + (pbRecvMsg.timestamp.nsec / 1000000)
        pbSend.reportmsg.src = pbRecvMsg.src
        print "pbRecvMsg.src:%s" % (pbRecvMsg.src)
        dictMsgInfoRecord['reportmsg']['src'] = pbRecvMsg.src
        pbSend.reportmsg.level = pbRecvMsg.level
        print "pbRecvMsg.level%s" % (pbRecvMsg.level)
        dictMsgInfoRecord['reportmsg']['level'] = pbRecvMsg.level
        pbSend.reportmsg.msg = pbRecvMsg.msg
        #print "pbRecvMsg.msg:%s" % (pbRecvMsg.msg)
        dictMsgInfoRecord['reportmsg']['msg'] = pbRecvMsg.msg
        pbSend.reportmsg.code = pbRecvMsg.code
        print "pbRecvMsg.code:%s" % (pbRecvMsg.code)
        dictMsgInfoRecord['reportmsg']['code'] = pbRecvMsg.code
        listTempResult = []
        listTempAction = []
        for elemResult in pbRecvMsg.result:
            listTempResult.append(elemResult)
            print "elemResult:%s" % (elemResult)
            pbSend.reportmsg.result.append(str(elemResult))
        for elemAction in pbRecvMsg.actions:
            listTempAction.append(elemAction)
            print "elemAction:%s" % (elemAction)
            pbSend.reportmsg.actions.append(str(elemAction))
        dictMsgInfoRecord['reportmsg']['result'] = listTempResult
        dictMsgInfoRecord['reportmsg']['actions'] = listTempAction

        print  listTempAction
        print  listTempResult
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
        print "code_version:%s" % (pbSend.carinfo.code_version)

        strBuffer = pbSend.SerializeToString()
        rosMessage = BinaryData()
        rosMessage.data = strBuffer
        rosMessage.size = len(strBuffer)
    except Exception as e:
        print "Exception happend "
        print   "exception happend"
        print   e.message
        print   str(e)
        print   'str(Exception):\t', str(Exception)
        print   'str(e):\t\t', str(e)
        print   'repr(e):\t', repr(e)
        print   'e.message:\t', e.message
        print   'traceback.print_exc():'
        traceback.print_exc()
        print   'traceback.format_exc():\n%s' % (traceback.format_exc())

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
                    print "finish write info to local disk"
                break
            if pbSend.reportmsg.level == "error":
                with open('/home/mogo/data/log/filebeat_upload/msg_record.log', 'ab+') as f:
                    f.write(strJson)
                    f.write('\n')
                    print "finish write error to local disk"
                break
            break
    except IOError:
        print  "operate file failed"
        exit(-1)
    # while True:
    #     if pbSend.reportmsg.level == "info":
    #         print "enter info"
    #         try:
    #             globalPubToTelematicsInfo.publish(msg)
    #         except  Exception as e:
    #             print " globalPubToTelematicsInfo.publish happend exception"
    #
    #         print "finish send info log "
    #         break
    #     if pbSend.reportmsg.level == "error":
    #         print "enter error"
    #         try:
    #             globalPubToTelematicsError.publish(msg)
    #         except Exception as e:
    #             print "globalPubToTelematicsError.publish happend exception"
    #         print "finish send error log "
    #         break
    #     break


def topicHzRecvCallback(msg):
    print "--------------------------------------------------recv from channel  /autopilot_info/topic_hz "
    rospy.loginfo("node: %s, topic: %s, type: %d, start: %d, hz: %f, max_delay: %d",msg.node, msg.topic, msg.type, msg.start, msg.hz, msg.max_delay)
    globalTopicHzPool.submit(task_topic_hz, msg)


def topicMsgCallback(msg):
    print "--------------------------------------------------recv from channel /autopilot_info/report_msg_info or /topilot_info/report_msg_error "
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
            print "#########################=================================write finished cpu_info.log"
    except IOError:
        print "operate file  cpu_info.log failed"
        exit(-1)
    pass


def topicCpuStatusCallback(msg):
    print "--------------------------------------------------recv from channel /monitor_process/sysinfo/cpu/status "
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
    print "recv node status from mac:{0},ip: {1}".format(strMac, strIp)
    print "#################################################################   dictTempInfo['data']"
    print dictTempInfo['data']
    print len(dictTempInfo['data'])
    print "#################################################################   dictTempInfo['data']"
    dictSaveToFile["timestamp"]["sec"] = rospy.Time.now().secs
    if len(dictTempInfo['data']) > 0:
        for key, value in dictTempInfo['data'].items():
            globalDictTableNodeHealth[key] = value
            globalDictTableNodeHealthTimeout[key] = dictSaveToFile["timestamp"]["sec"]
    print "########################################   now task_node_health len : %d " % len(globalDictHostMacInfo)
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
    print "strJsonSaveToFile: %s" % strJsonSaveToFile
    try:
        folder_check()
        with open('/home/mogo/data/log/filebeat_upload/node_health.log', 'a+') as f:
            f.write(strJsonSaveToFile)
            f.write("\n")
            globalPubOperatorToolNodeHealth.publish(rosSendMsg)
            print "#########################=================================write finished node_health.log"
    except IOError:
        print "operate file node_health.log failed"
        exit(-1)
    pass


def topicNodeStatusCallback(msg):
    print "--------------------------------------------------recv from channel /monitor_process/sysinfo/nodes/status"
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
            print "#########################=================================write finished memory_info.log"
    except IOError:
        print "operate file memory_info.log  failed"
        exit(-1)
    pass


def topicMemoryStatusCallback(msg):
    print "--------------------------------------------------recv from channel /monitor_process/sysinfo/memory/status "
    if msg.size > 0:
        globalMemInfoPool.submit(task_memory_info, msg)


def autopilotModeCallback(msg):
    # print "msg.size()=%d" %(msg.size)
    pbStatus = common_vehicle_state_pb2.VehicleState()
    pbStatus.ParseFromString(msg.data)
    # print "vStatus.pilot_mode=%d" %(pbStatus.pilot_mode)
    # print (type(pbStatus.pilot_mode))

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


def addLocalizationListener():
    rospy.Subscriber("/autopilot_info/topic_hz", TopicHz, topicHzRecvCallback)
    rospy.Subscriber("/autopilot_info/report_msg_info", BinaryData, topicMsgCallback)
    rospy.Subscriber("/autopilot_info/report_msg_error", BinaryData, topicMsgCallback)
    rospy.Subscriber("/monitor_process/sysinfo/cpu/status", BinaryData, topicCpuStatusCallback)
    rospy.Subscriber("/monitor_process/sysinfo/memory/status", BinaryData, topicMemoryStatusCallback)
    rospy.Subscriber("/monitor_process/sysinfo/nodes/status", BinaryData, topicNodeStatusCallback)
    rospy.Subscriber('/chassis/vehicle_state', BinaryData, autopilotModeCallback)


# def threadSendControlCmd(strThreadName, intDelay):
#     while True:
#         rosControlMsg = BinaryData()
#         strUuid = str(uuid.uuid1())
#         # print type(strUuid)
#         # print strUuid
#         rosControlMsg.data = strUuid
#         rosControlMsg.size = len(rosControlMsg.data)
#         rospy.Time.now().secs
#         print "+++++++++++++++++++++++++++++++++=%d.%d  threadSendControlCmd publish ControlCmd .......Request_Uuid:%s " % (
#             rospy.Time.now().secs, rospy.Time.now().nsecs, strUuid)
#         globalPubToMonitorProcessControlCmd.publish(rosControlMsg)
#         time.sleep(intDelay)


def threadTimeoutRestNodeStatus(strThreadName, intDelay):
    while True:
        intCurrentSec = rospy.Time.now().secs
        global globalDictTableNodeHealthTimeout
        global globalDictTableNodeHealth
        for key, value in globalDictTableNodeHealthTimeout.items():
            if (intCurrentSec - value) > intDelay:
                globalDictTableNodeHealth[key] = "off"
                rospy.logerr("node has timeout: " + key)
        time.sleep(intDelay)


def startThreadControlCmd(intTimeVal):
    try:
        thread.start_new_thread(threadTimeoutRestNodeStatus, ("ControlCmd", int(intTimeVal),))
    except:
        print "Error: unable to start thread"

def flushTopicHzWriterBuffer():
    global globalListWaitWriteBuffer
    try:
        folder_check()
        with open('/home/mogo/data/log/filebeat_upload/topic_hz_log.log', 'ab+') as f:
            if len(globalListWaitWriteBuffer) > 0:
                for line in globalListWaitWriteBuffer:
                    f.write(line)
                    f.write('\n')
            print  "================================flushTopicHzWriterBuffer write  local disk finished "
            globalListWaitWriteBuffer = []
            print "flushTopicHzWriterBuffer: after flush to  file , globalListWaitWriteBuffer :{0}".format(globalListWaitWriteBuffer)
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

def threadFlushTopicHz(intTimeVal):
    while True:
        print "start check WaitWriteBuffer"
        flushTopicHzWriterBuffer()
        time.sleep(30)


def startThreadFlushWaitWriteBufferCmd(intTimeVal):
    try:
        thread.start_new_thread(threadFlushTopicHz, (int(intTimeVal),))
    except Exception as e:
        print "exception happend"
        print  e.message
        print   str(e)
        print   'str(Exception):\t', str(Exception)
        print   'str(e):\t\t', str(e)
        print   'repr(e):\t', repr(e)
        print   'e.message:\t', e.message
        print   'traceback.print_exc():'
        traceback.print_exc()
        print  'traceback.format_exc():\n%s' % (traceback.format_exc())

def main():
    global listSubScriptHzItem
    listSubScriptHzItem.append("/app1")
    listSubScriptHzItem.append("/app3")
    # initial node
    globalCommonPara.initPara()
    rospy.init_node('monitor_collect', anonymous=True)

    global globalDelayTimeInterval
    globalDelayTimeInterval = 10
    # strFullParaName = "%s/detect_interval" % (rospy.get_name())
    # print "strFullParaName:%s" % strFullParaName
    # temp = rospy.get_param(strFullParaName)
    # if temp <= 0:
    #     globalDelayTimeInterval = 5
    # else:
    #     globalDelayTimeInterval = temp
    # print "=============================set globalDelayTimeInterval:%d" % globalDelayTimeInterval
    # add listener
    addLocalizationListener()
    startThreadControlCmd(globalDelayTimeInterval)
    startThreadFlushWaitWriteBufferCmd(30)
    ## wait msg
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
