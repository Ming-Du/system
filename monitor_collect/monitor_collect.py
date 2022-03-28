#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import proto.mogo_report_msg_pb2  as comon_mogo_report_msg_pb2
from  entity.LocInfo import  LocInfo
from entity.CommonPara import  CommonPara

from threading import Thread
import threading
from concurrent.futures import ThreadPoolExecutor
import json
from entity.CollectVehicleInfo import   CollectVehicleInfo
import proto.mogo_report_msg_pb2  as common_mogo_report_msg_pb2
import proto.monitor_msg_pb2 as  common_monitor_msg_pb2
import proto.monitor_topic_hz_pb2 as monitor_topic_hz_pb2
import collections
import json
from os import path, access, R_OK
import os, sys, stat


### global area
globalTopicHzPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalTopicHzPool')
globalTopicMsgPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalTopicMsgPool')
globalCollectVehicleInfo  = CollectVehicleInfo()
globalCommonPara = CommonPara()
globalPubToTelematicsInfo=rospy.Publisher("/autopilot_info/report_msg_info",BinaryData,queue_size=100)
globalPubToTelematicsError=rospy.Publisher("/autopilot_info/report_msg_error",BinaryData,queue_size=100)
globalPubToTelematicsTopicHz=rospy.Publisher("/cloud_debug/report_topic_hz",BinaryData,queue_size=100)
rDictHzTable = {}
listSubScriptHzItem =  []
global_hz_time_write_interval = 0

def folder_check():
    PATH='/home/mogo/data/log/filebeat_upload/'
    if os.path.isdir(PATH) and access(PATH, R_OK):
        print "folder exists and is readable"
    else:
        print "folder not ready,now create path"
        os.makedirs(PATH)
        print os.path.isdir(PATH)
        os.chmod(PATH,0777)

def task_topic_hz(msg):
    print "++++++++++++++++++++++++"
    tree = lambda: collections.defaultdict(tree)
    dictHzRecord = tree()
    try:
        global global_hz_time_write_interval
        pbTopicHz = common_log_reslove_pb2.PubLogInfo()
        pbTopicHz.ParseFromString(msg.data)
        pbMonitorHzWidthCarInfo  = monitor_topic_hz_pb2.MonitorTopicHz()
        global rDictHzTable
        for elemHz   in pbTopicHz.topic_hz:
            rDictHzTable[elemHz.name]=elemHz.hz
            print elemHz.name
            print elemHz.hz
        pbMonitorHzWidthCarInfo.pLogInfo.header.seq  = pbTopicHz.header.seq
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.seq:%d" %(pbMonitorHzWidthCarInfo.pLogInfo.header.seq)
        dictHzRecord["log_type"]="topic_hz"
        dictHzRecord['pLogInfo']['header']['seq']=(pbTopicHz.header.seq)
        pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.sec  = pbTopicHz.header.stamp.sec
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.sec:%d" %(pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.sec)
        dictHzRecord['pLogInfo']['header']['stamp']['sec']=(pbTopicHz.header.stamp.sec)
        pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.nsec  = pbTopicHz.header.stamp.nsec
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.nsec:%d" %(pbMonitorHzWidthCarInfo.pLogInfo.header.stamp.nsec)
        dictHzRecord['pLogInfo']['header']['stamp']['nsec']=(pbTopicHz.header.stamp.nsec)
        pbMonitorHzWidthCarInfo.pLogInfo.header.frame_id = pbTopicHz.header.frame_id
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.frame_id:%s " %(pbMonitorHzWidthCarInfo.pLogInfo.header.frame_id)
        dictHzRecord['pLogInfo']['header']['frame_id']=(pbTopicHz.header.frame_id)
        print "=================================="
        pbMonitorHzWidthCarInfo.pLogInfo.header.module_name = pbTopicHz.header.module_name
        print "pbMonitorHzWidthCarInfo.pLogInfo.header.module_name:%s" %(pbMonitorHzWidthCarInfo.pLogInfo.header.module_name)
        dictHzRecord['pLogInfo']['header']['module_name']= pbTopicHz.header.module_name
        pbMonitorHzWidthCarInfo.pLogInfo.start_stamp = pbTopicHz.start_stamp
        print "pbMonitorHzWidthCarInfo.pLogInfo.start_stamp:%f" %(pbMonitorHzWidthCarInfo.pLogInfo.start_stamp)
        dictHzRecord['pLogInfo']['start_stamp']=pbTopicHz.start_stamp
        pbMonitorHzWidthCarInfo.pLogInfo.end_stamp = pbTopicHz.end_stamp
        print "pbMonitorHzWidthCarInfo.pLogInfo.end_stamp:%f" %( pbMonitorHzWidthCarInfo.pLogInfo.end_stamp)
        dictHzRecord['pLogInfo']['end_stamp']=pbTopicHz.end_stamp
        # for k,v in  rDictHzTable.items():
        #     if k in listSubScriptHzItem:
        #         hzItem = pbMonitorHzWidthCarInfo.pLogInfo.topic_hz.add()
        #         hzItem.name = k
        #         hzItem.hz = v
        #         print "send:%s" % (k)
        listHzCollect  = []
        for k,v in  rDictHzTable.items():
            dictHzUnit= {}
            hzItem = pbMonitorHzWidthCarInfo.pLogInfo.topic_hz.add()
            hzItem.name = k
            dictHzUnit['name']=hzItem.name
            hzItem.hz = v
            dictHzUnit['hz']=hzItem.hz
            listHzCollect.append(dictHzUnit)
            # print "send:%s" % (k)
        dictHzRecord['pLogInfo']['topic_hz']=listHzCollect
        pbMonitorHzWidthCarInfo.carinfo.car_type= globalCommonPara.dictCarInfo['car_type']
        dictHzRecord['carinfo']['car_type']=globalCommonPara.dictCarInfo['car_type']
        pbMonitorHzWidthCarInfo.carinfo.code_version = globalCommonPara.dictCarInfo['code_version']
        dictHzRecord['carinfo']['code_version']=globalCommonPara.dictCarInfo['code_version']
        pbMonitorHzWidthCarInfo.carinfo.car_plate = globalCommonPara.dictCarInfo['car_plate']
        dictHzRecord['carinfo']['car_plate']= globalCommonPara.dictCarInfo['car_plate']
        print "??????????????????????????????????car_plate:%s"  %(dictHzRecord['carinfo']['car_plate'])
        print "before dest buffer file "
        strDestPbBufferToFile = pbMonitorHzWidthCarInfo.SerializeToString()
        print "before rebuild rosmsg"
        rosMessage = BinaryData()
        rosMessage.data = strDestPbBufferToFile
        rosMessage.size = len(strDestPbBufferToFile)
        global_hz_time_write_interval = global_hz_time_write_interval + 1
    except Exception as e :
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():'; traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())

    print dictHzRecord
    strJson = json.dumps(dictHzRecord)
    print "strJson:%s" %(strJson)

    ## Write dest file
    print "global_hz_time_write_interval:%d " %(global_hz_time_write_interval)
    print "#######################start write hz to log"
    try:
        folder_check()
        with open('/home/mogo/data/log/filebeat_upload/topic_hz_log.log', 'ab+') as f:
            f.write(strJson)
            f.write('\n')

            print "write  local disk finished "
    except IOError:
        print  "operate file failed"
        exit(-1)
    print "before send "

    try:
        globalPubToTelematicsTopicHz.publish(msg)
        print "finish send message"
        print "send size : %d" %(msg.size)
    except Exception as e:
        print "globalPubToTelematicsTopicHz.publish happend exeception"



def task_topic_msg(msg):
    tree = lambda: collections.defaultdict(tree)
    dictMsgInfoRecord = tree()
    try:
        pbRecvMsg = comon_mogo_report_msg_pb2.MogoReportMessage()
        pbRecvMsg.ParseFromString(msg.data)
        pbSend  = common_monitor_msg_pb2.MonitorMsg()
        pbSend.reportmsg.timestamp.sec = pbRecvMsg.timestamp.sec
        print "timestamp.sec:%d" %(pbRecvMsg.timestamp.sec)
        dictMsgInfoRecord['reportmsg']['timestamp']['sec']=pbRecvMsg.timestamp.sec

        pbSend.reportmsg.timestamp.nsec = pbRecvMsg.timestamp.nsec
        print "timestamp.nsec:%d" %(pbRecvMsg.timestamp.nsec)
        dictMsgInfoRecord['reportmsg']['timestamp']['nsec']=pbRecvMsg.timestamp.nsec
        pbSend.reportmsg.src = pbRecvMsg.src
        print "pbRecvMsg.src:%s" % (pbRecvMsg.src)
        dictMsgInfoRecord['reportmsg']['src']=pbRecvMsg.src
        pbSend.reportmsg.level = pbRecvMsg.level
        print "pbRecvMsg.level%s" % (pbRecvMsg.level)
        dictMsgInfoRecord['reportmsg']['level']=pbRecvMsg.level
        pbSend.reportmsg.msg = pbRecvMsg.msg
        print "pbRecvMsg.msg:%s" %(pbRecvMsg.msg)
        dictMsgInfoRecord['reportmsg']['msg']=pbRecvMsg.msg
        pbSend.reportmsg.code = pbRecvMsg.code
        print "pbRecvMsg.code:%s" % (pbRecvMsg.code)
        dictMsgInfoRecord['reportmsg']['code']=pbRecvMsg.code
        listTempResult = []
        listTempAction = []
        for elemResult in pbRecvMsg.result:
            listTempResult.append(elemResult)
            print "elemResult:%s" %(elemResult)
            pbSend.reportmsg.result.append(str(elemResult))
        for elemAction in pbRecvMsg.actions:
            listTempAction.append(elemAction)
            print "elemAction:%s" %(elemAction)
            pbSend.reportmsg.actions.append(str(elemAction))
        dictMsgInfoRecord['reportmsg']['result']=listTempResult
        dictMsgInfoRecord['reportmsg']['actions']=listTempAction

        print  listTempAction
        print  listTempResult
        pbSend.carinfo.car_plate = globalCommonPara.dictCarInfo["car_plate"]
        dictMsgInfoRecord['carinfo']['car_plate']=globalCommonPara.dictCarInfo["car_plate"]
        pbSend.carinfo.car_type       = globalCommonPara.dictCarInfo["car_type"]
        dictMsgInfoRecord['carinfo']['car_type']=globalCommonPara.dictCarInfo["car_type"]
        pbSend.carinfo.code_version   = globalCommonPara.dictCarInfo["code_version"]
        dictMsgInfoRecord['carinfo']['code_version']=globalCommonPara.dictCarInfo["code_version"]
        while True:
            if pbSend.reportmsg.level == "info":
                dictMsgInfoRecord['log_type']="info_log"
                break
            if pbSend.reportmsg.level == "error":
                dictMsgInfoRecord['log_type']="error_log"
                break
            break
        print "code_version:%s" %(pbSend.carinfo.code_version)

        strBuffer = pbSend.SerializeToString()
        rosMessage = BinaryData()
        rosMessage.data = strBuffer
        rosMessage.size = len(strBuffer)
    except Exception as e :
        print "Exception happend "

    strJson = json.dumps(dictMsgInfoRecord)
    ## send telematics
    # /autopilot_info/report_msg_error
    # /autopilot_info/report_msg_info
    ## Write dest file
    try:
        folder_check()
        while True:
            if pbSend.reportmsg.level == "info":
                with open('/home/mogo/data/log/filebeat_upload/msg_info_log.log', 'ab+') as f:
                    f.write(strJson)
                    f.write('\n')
                    print "finish write info to local disk"
                break
            if pbSend.reportmsg.level == "error":
                with open('/home/mogo/data/log/febeat_upload/msg_error_log.log', 'ab+') as f:
                    f.write(strJson)
                    f.write('\n')
                    print "finish write error to local disk"
                break
            break
    except IOError:
        print  "operate file failed"
        exit(-1)
    while True:
        if pbSend.reportmsg.level == "info":
            print "enter info"
            try:
                globalPubToTelematicsInfo.publish(msg)
            except  Exception as e :
                print " globalPubToTelematicsInfo.publish happend exception"

            print "finish send info log "
            break
        if pbSend.reportmsg.level  == "error":
            print "enter error"
            try:
                globalPubToTelematicsError.publish(msg)
            except Exception as e :
                print "globalPubToTelematicsError.publish happend exception"
            print "finish send error log "
            break
        break



def topicHzRecvCallback(msg):
    print "--------------------------------------------------recv from channel  /autopilot_info/report_topic_hz "
    if msg.size >  0 :
        globalTopicHzPool.submit(task_topic_hz,msg)

def topicMsgCallback(msg):
    print "--------------------------------------------------recv from channel /autopilot_info/report_msg_info or /topilot_info/report_msg_error "
    if msg.size >  0 :
        globalTopicMsgPool.submit(task_topic_msg,msg)

def addLocalizationListener():
    rospy.Subscriber("/autopilot_info/internal/report_topic_hz",BinaryData,topicHzRecvCallback)
    rospy.Subscriber("/autopilot_info/internal/report_msg_info",BinaryData,topicMsgCallback)
    rospy.Subscriber("/autopilot_info/internal/report_msg_error", BinaryData, topicMsgCallback)

def main():
    global listSubScriptHzItem
    listSubScriptHzItem.append("/app1")
    listSubScriptHzItem.append("/app3")
    # initial node
    globalCommonPara.initPara()
    rospy.init_node('monitor_collect', anonymous=True)
    # add listener
    addLocalizationListener()
    ## wait msg
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
