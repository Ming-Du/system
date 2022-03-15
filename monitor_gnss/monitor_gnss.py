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
from  entity.LocInfo import  LocInfo
from entity.CommonPara import  CommonPara

from threading import Thread
import threading
from concurrent.futures import ThreadPoolExecutor
import json
from entity.CollectVehicleInfo import   CollectVehicleInfo


globalLocationPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_Location')
globalCollectVehicleInfo  = CollectVehicleInfo()
globalCommonPara = CommonPara()
globalLastMicroSec = 0
globalListPostion = []
globalWriteInterval = 50


def task_localization(pb_msg):
    thread_name = threading.current_thread().getName()
    location = common_localization.Localization()
    location.ParseFromString(pb_msg)
    instanceLocInfoUnit = LocInfo()
    instanceLocInfoUnit.MarkMapPosition_x = location.position.x
    instanceLocInfoUnit.MarkMapPosition_y = location.position.y
    instanceLocInfoUnit.MarkMapPosition_longitude = location.longitude
    instanceLocInfoUnit.MarkMapPosition_latitude = location.latitude
    instanceLocInfoUnit.sec =  (location.header.stamp.sec)
    instanceLocInfoUnit.nsec = (location.header.stamp.nsec)

    # print "get name:%s,longitude:%f,latitude:%f x: %f, y: %f,sec: %d , nsec:%d " % (thread_name, instanceLocInfoUnit.MarkMapPosition_longitude,instanceLocInfoUnit.MarkMapPosition_latitude,
    #                                                                                 instanceLocInfoUnit.MarkMapPosition_x,instanceLocInfoUnit.MarkMapPosition_y,
    #                                                                                 instanceLocInfoUnit.sec,
    #                                                                                 instanceLocInfoUnit.nsec)

    dictPostionLog={}
    #dictPostionLog["sec"]=instanceLocInfoUnit.sec
    #dictPostionLog["nsec"]=instanceLocInfoUnit.nsec
    # dictInfoLog["car_info"]=globalCommonPara.dictCarInfo
    dictPostionLog["pilotMode"]=int(globalCollectVehicleInfo.int_pilot_mode)
    dictPostionLog["takeover_reason_code"] = int(globalCollectVehicleInfo.int_error_code)
    dictPostionLog["takeover_reason_message"]=str(globalCollectVehicleInfo.str_err_msg)
    dictPostionLog["position_x"]=instanceLocInfoUnit.MarkMapPosition_x
    dictPostionLog["position_y"]=instanceLocInfoUnit.MarkMapPosition_y
    dictPostionLog["location_longitude"]=instanceLocInfoUnit.MarkMapPosition_longitude
    dictPostionLog["location_latitude"]= instanceLocInfoUnit.MarkMapPosition_latitude
    CurrentMicroSec = instanceLocInfoUnit.sec*1000 + instanceLocInfoUnit.nsec/1000000
    dictPostionLog["msec"] = CurrentMicroSec

    print "before while"
    global globalListPostion
    global globalLastMicroSec
    print '=========c:%d---g:%d---len:%d' %(CurrentMicroSec,globalLastMicroSec,len(globalListPostion))
    while True:
        if globalLastMicroSec == 0:
            print "enter first update globalLastMicroSec"
            globalListPostion.append(dictPostionLog)
            ## update last micro sec
            globalLastMicroSec = CurrentMicroSec
            break
        if (CurrentMicroSec  - globalLastMicroSec >  globalWriteInterval ) or  (CurrentMicroSec  - globalLastMicroSec == globalWriteInterval ):
            print "enter second globalLastMicroSec"
            globalListPostion.append(dictPostionLog)
            ### update  last micro sec
            globalLastMicroSec = CurrentMicroSec
            break
        break
    #print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    if (len(globalListPostion)  >  (1000/globalWriteInterval) )  or   ( len(globalListPostion) == (1000/globalWriteInterval) ):
        dictLogInfo = {}
        dictLogInfo["car_info"]=globalCommonPara.dictCarInfo
        dictLogInfo["positions"]=globalListPostion
        strJsonLineContent = json.dumps(dictPostionLog)
        # print strJsonLineContent
        #print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        try:
            with open('/home/mogo/data/log/location.txt', 'a+') as f:
                #print "dddddddddddddddddddddddd"
                f.write(strJsonLineContent)
                f.write("\n")
                #global globalListPostion
                #print "eeeeeeeeeeeeeeeeeeeeee"
                globalListPostion=[]
                #print "cccccccccccccccccccccccccccc"
                print "#########################=================================write finished, now clean globalListPostion"
        except IOError:
            print "operate file failed"
            exit(-1)



def localizationCallback(msg):
    #print(msg.name)
    #print(msg.size)
    if msg.size > 0:
        globalLocationPool.submit(task_localization, msg.data)



def autopilotModeCallback(msg):
    #print "msg.size()=%d" %(msg.size)
    pbStatus=common_vehicle_state_pb2.VehicleState()
    pbStatus.ParseFromString(msg.data)
    #print "vStatus.pilot_mode=%d" %(pbStatus.pilot_mode)
    #print (type(pbStatus.pilot_mode))

    global globalCollectVehicleInfo
    globalCollectVehicleInfo = CollectVehicleInfo()
    (globalCollectVehicleInfo.int_pilot_mode) = pbStatus.pilot_mode
    (globalCollectVehicleInfo.b_steer_inference) = pbStatus.steer_inference
    (globalCollectVehicleInfo.b_brake_inference)= pbStatus.brake_inference
    (globalCollectVehicleInfo.b_accel_inference)  = pbStatus.accel_inference
    globalCollectVehicleInfo.b_gear_switch_inference = pbStatus.gear_switch_inference
    globalCollectVehicleInfo.b_location_missing  =  pbStatus.location_missing
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
        if globalCollectVehicleInfo.b_chassis_status_missing :
            globalCollectVehicleInfo.int_error_code = 7
            globalCollectVehicleInfo.str_err_msg="lostchassis"
            break
        break

def addLocalizationListener():
    rospy.Subscriber('/localization/global', BinaryData, localizationCallback)
    rospy.Subscriber('/chassis/vehicle_state', BinaryData, autopilotModeCallback)

def main():
    # initial node
    globalCommonPara.initPara()
    rospy.init_node('monitor_gnss', anonymous=True)
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
