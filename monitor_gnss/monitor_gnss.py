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
from os import path, access, R_OK
import os, sys, stat

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
globalVihiclePool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_vehicle')
globalCollectVehicleInfo  = CollectVehicleInfo()
globalCommonPara = CommonPara()
globalLastMicroSec = 0
globalListPostion = []
globalWriteInterval = 50


globalLastMicroSec_vehicle_status = 0
globalListPostion_vehicle_status = []
globalWriteInterval_vehicle_status = 50

def folder_check():
    PATH='/home/mogo/data/log/filebeat_upload/'
    if os.path.isdir(PATH) and access(PATH, R_OK):
        pass
    else:
        rospy.logwarn("folder not ready,now create path")
        os.makedirs(PATH)
        os.chmod(PATH,0777)


def task_localization(pb_msg):
    thread_name = threading.current_thread().getName()
    location = common_localization.Localization()
    location.ParseFromString(pb_msg)
    instanceLocInfoUnit = LocInfo()
    instanceLocInfoUnit.MarkMapPosition_x = location.position.x
    instanceLocInfoUnit.MarkMapPosition_y = location.position.y
    instanceLocInfoUnit.MarkMapPosition_longitude = location.longitude
    instanceLocInfoUnit.MarkMapPosition_latitude = location.latitude
    instanceLocInfoUnit.roll=location.roll
    instanceLocInfoUnit.pitch=location.pitch
    instanceLocInfoUnit.yaw=location.yaw
    instanceLocInfoUnit.roll_v=location.roll_v
    instanceLocInfoUnit.pitch_v=location.pitch_v
    instanceLocInfoUnit.yaw_v=location.yaw_v
    instanceLocInfoUnit.lateral_v=location.lateral_v
    instanceLocInfoUnit.longitudinal_v=location.longitudinal_v
    instanceLocInfoUnit.vertical_v=location.vertical_v
    instanceLocInfoUnit.lateral_a=location.lateral_a
    instanceLocInfoUnit.longitudinal_a=location.longitudinal_a
    instanceLocInfoUnit.vertical_a=location.vertical_a
    instanceLocInfoUnit.horizontal_v=location.horizontal_v
    instanceLocInfoUnit.utm_zone=location.utm_zone
    instanceLocInfoUnit.gnss_sys_dtime=location.gnss_sys_dtime
    instanceLocInfoUnit.sec =  (location.header.stamp.sec)
    instanceLocInfoUnit.nsec = (location.header.stamp.nsec)


    dictPostionLog={}
    dictPostionLog["pilotMode"]=int(globalCollectVehicleInfo.int_pilot_mode)
    dictPostionLog["takeover_reason_code"] = int(globalCollectVehicleInfo.int_error_code)
    dictPostionLog["takeover_reason_message"]=str(globalCollectVehicleInfo.str_err_msg)
    dictPostionLog["position_x"]=instanceLocInfoUnit.MarkMapPosition_x
    dictPostionLog["position_y"]=instanceLocInfoUnit.MarkMapPosition_y
    dictPostionLog["location_longitude"]=instanceLocInfoUnit.MarkMapPosition_longitude
    dictPostionLog["location_latitude"]= instanceLocInfoUnit.MarkMapPosition_latitude

    dictPostionLog["roll"] = instanceLocInfoUnit.roll
    dictPostionLog["pitch"] = instanceLocInfoUnit.pitch
    dictPostionLog["yaw"] = instanceLocInfoUnit.yaw
    dictPostionLog["roll_v"] = instanceLocInfoUnit.roll_v
    dictPostionLog["pitch_v"] = instanceLocInfoUnit.pitch_v
    dictPostionLog["yaw_v"] = instanceLocInfoUnit.yaw_v
    dictPostionLog["lateral_v"] = instanceLocInfoUnit.lateral_v
    dictPostionLog["longitudinal_v"] = instanceLocInfoUnit.longitudinal_v
    dictPostionLog["vertical_v"] = instanceLocInfoUnit.vertical_v
    dictPostionLog["lateral_a"] = instanceLocInfoUnit.lateral_a
    dictPostionLog["longitudinal_a"] = instanceLocInfoUnit.longitudinal_a

    dictPostionLog["vertical_a"] = instanceLocInfoUnit.vertical_a
    dictPostionLog["horizontal_v"] = instanceLocInfoUnit.horizontal_v
    dictPostionLog["utm_zone"] = instanceLocInfoUnit.utm_zone
    dictPostionLog["gnss_sys_dtime"] = instanceLocInfoUnit.gnss_sys_dtime


    CurrentMicroSec = instanceLocInfoUnit.sec*1000 + instanceLocInfoUnit.nsec/1000000
    dictPostionLog["msec"] = CurrentMicroSec


    global globalListPostion
    global globalLastMicroSec

    while True:
        if globalLastMicroSec == 0:

            rospy.logdebug_throttle(5,"enter first update globalLastMicroSec")
            globalListPostion.append(dictPostionLog)
            ## update last micro sec
            globalLastMicroSec = CurrentMicroSec
            break
        if (CurrentMicroSec  - globalLastMicroSec >  globalWriteInterval ) or  (CurrentMicroSec  - globalLastMicroSec == globalWriteInterval ):
            rospy.logdebug_throttle(5, "enter first update globalLastMicroSec")
            globalListPostion.append(dictPostionLog)
            ### update  last micro sec
            globalLastMicroSec = CurrentMicroSec
            break
        break

    if (len(globalListPostion)  >  (1000/globalWriteInterval) )  or   ( len(globalListPostion) == (1000/globalWriteInterval) ):
        tree = lambda: collections.defaultdict(tree)
        dictLogInfo = tree()
        dictLogInfo["log_type"]="location"
        curSec = rospy.rostime.Time.now().secs
        curNsec = rospy.rostime.Time.now().nsecs
        dictLogInfo["timestamp"]['sec']=curSec
        dictLogInfo["timestamp"]["nsec"]=curNsec
        dictLogInfo["car_info"]=globalCommonPara.dictCarInfo
        dictLogInfo["positions"]=globalListPostion
        strJsonLineContent = json.dumps(dictLogInfo)

        try:
            folder_check()
            with open('/home/mogo/data/log/filebeat_upload/location.log', 'a+') as f:

                f.write(strJsonLineContent)
                f.write("\n")
        except IOError:
            rospy.logwarn("operate file failed")
            exit(-1)



def localizationCallback(msg):
    if msg.size > 0:
        globalLocationPool.submit(task_localization, msg.data)

def task_vehicle(pb_msg):
    pbStatus = common_vehicle_state_pb2.VehicleState()
    pbStatus.ParseFromString(pb_msg)
    instanceVehicleInfo = CollectVehicleInfo()
    instanceVehicleInfo.int_pilot_mode = pbStatus.pilot_mode
    instanceVehicleInfo.b_steer_inference = pbStatus.steer_inference
    instanceVehicleInfo.b_brake_inference = pbStatus.brake_inference
    instanceVehicleInfo.b_accel_inference = pbStatus.accel_inference
    instanceVehicleInfo.b_gear_switch_inference = pbStatus.gear_switch_inference
    instanceVehicleInfo.b_location_missing = pbStatus.location_missing
    instanceVehicleInfo.b_trajectory_missing = pbStatus.trajectory_missing
    instanceVehicleInfo.b_chassis_status_missing = pbStatus.chassis_status_missing
    instanceVehicleInfo.brake_light_status = pbStatus.brake_light_status
    instanceVehicleInfo.pilot_mode_condition_met = pbStatus.pilot_mode_condition_met
    instanceVehicleInfo.steeringSpd = pbStatus.steeringSpds
    instanceVehicleInfo.leftFrontWheelAngle = pbStatus.leftFrontWheelAngle
    instanceVehicleInfo.rightFrontWheelAngle = pbStatus.rightFrontWheelAngle
    instanceVehicleInfo.steering = pbStatus.steering
    instanceVehicleInfo.speed = pbStatus.speed
    instanceVehicleInfo.accel = pbStatus.accel
    instanceVehicleInfo.throttle = pbStatus.throttle
    instanceVehicleInfo.brake = pbStatus.brake
    instanceVehicleInfo.gear = pbStatus.gear
    instanceVehicleInfo.light = pbStatus.light
    instanceVehicleInfo.horn = pbStatus.horn
    instanceVehicleInfo.highbeam = pbStatus.highbeam
    instanceVehicleInfo.lowbeam = pbStatus.lowbeam
    instanceVehicleInfo.foglight = pbStatus.foglight
    instanceVehicleInfo.clearance_lamps = pbStatus.clearance_lamps
    instanceVehicleInfo.warn_light = pbStatus.warn_light
    instanceVehicleInfo.parking_brake = pbStatus.parking_brake
    instanceVehicleInfo.longitude_driving_mode = pbStatus.longitude_driving_mode
    instanceVehicleInfo.eps_steering_mode = pbStatus.eps_steering_mode
    instanceVehicleInfo.steering_sign = pbStatus.steering_sign

    dictVehicleLog = {}
    dictVehicleLog['int_pilot_mode'] = instanceVehicleInfo.pilot_mode
    dictVehicleLog['b_steer_inference'] = instanceVehicleInfo.steer_inference
    dictVehicleLog['b_brake_inference'] = instanceVehicleInfo.brake_inference
    dictVehicleLog['b_accel_inference'] = instanceVehicleInfo.accel_inference
    dictVehicleLog['b_gear_switch_inference'] = instanceVehicleInfo.gear_switch_inference
    dictVehicleLog['b_location_missing'] = instanceVehicleInfo.location_missing
    dictVehicleLog['b_trajectory_missing'] = instanceVehicleInfo.trajectory_missing
    dictVehicleLog['b_chassis_status_missing'] = instanceVehicleInfo.chassis_status_missing
    dictVehicleLog['brake_light_status'] = instanceVehicleInfo.brake_light_status
    dictVehicleLog['pilot_mode_condition_met'] = instanceVehicleInfo.pilot_mode_condition_met
    dictVehicleLog['steeringSpd'] = instanceVehicleInfo.steeringSpds
    dictVehicleLog['leftFrontWheelAngle'] = instanceVehicleInfo.leftFrontWheelAngle
    dictVehicleLog['rightFrontWheelAngle'] = instanceVehicleInfo.rightFrontWheelAngle
    dictVehicleLog['steering'] = instanceVehicleInfo.steering
    dictVehicleLog['speed'] = instanceVehicleInfo.speed
    dictVehicleLog['accel'] = instanceVehicleInfo.accel
    dictVehicleLog['throttle'] = instanceVehicleInfo.throttle
    dictVehicleLog['brake'] = instanceVehicleInfo.brake
    dictVehicleLog['gear'] = instanceVehicleInfo.gear
    dictVehicleLog['light'] = instanceVehicleInfo.light
    dictVehicleLog['horn'] = instanceVehicleInfo.horn
    dictVehicleLog['highbeam'] = instanceVehicleInfo.highbeam
    dictVehicleLog['lowbeam'] = instanceVehicleInfo.lowbeam
    dictVehicleLog['foglight'] = instanceVehicleInfo.foglight
    dictVehicleLog['clearance_lamps'] = instanceVehicleInfo.clearance_lamps
    dictVehicleLog['warn_light'] = instanceVehicleInfo.warn_light
    dictVehicleLog['parking_brake'] = instanceVehicleInfo.parking_brake
    dictVehicleLog['longitude_driving_mode'] = instanceVehicleInfo.longitude_driving_mode
    dictVehicleLog['eps_steering_mode'] = instanceVehicleInfo.eps_steering_mode
    dictVehicleLog['steering_sign'] = instanceVehicleInfo.steering_sign
    sec = (pbStatus.header.stamp.sec)
    nsec = (pbStatus.header.stamp.nsec)

    CurrentMicroSec = sec*1000 + nsec/1000000
    dictVehicleLog['sec'] = sec
    dictVehicleLog['nsec'] = nsec
    dictVehicleLog["msec"] = CurrentMicroSec

    global globalListPostion_vehicle_status
    global globalLastMicroSec_vehicle_status

    while True:
        if globalLastMicroSec_vehicle_status == 0:
            rospy.logdebug_throttle(5, "enter first update globalLastMicroSec")
            globalListPostion_vehicle_status.append(dictVehicleLog)
            ## update last micro sec
            globalLastMicroSec_vehicle_status = CurrentMicroSec
            break
        if (CurrentMicroSec - globalLastMicroSec_vehicle_status > globalWriteInterval_vehicle_status) or (
                CurrentMicroSec - globalLastMicroSec_vehicle_status == globalWriteInterval_vehicle_status):
            rospy.logdebug_throttle(5, "enter first update globalLastMicroSec")
            globalListPostion_vehicle_status.append(dictVehicleLog)
            ### update  last micro sec
            globalLastMicroSec_vehicle_status = CurrentMicroSec
            break
        break

    if (len(globalListPostion_vehicle_status) > (1000 / globalWriteInterval_vehicle_status)) or (
            len(globalListPostion_vehicle_status) == (1000 / globalWriteInterval_vehicle_status)):
        tree = lambda: collections.defaultdict(tree)
        dictLogInfo = tree()
        dictLogInfo["log_type"] = "vehicle_status"
        curSec = rospy.rostime.Time.now().secs
        curNsec = rospy.rostime.Time.now().nsecs
        dictLogInfo["timestamp"]['sec'] = curSec
        dictLogInfo["timestamp"]["nsec"] = curNsec
        dictLogInfo["car_info"] = globalCommonPara.dictCarInfo
        dictLogInfo["content"] = globalListPostion_vehicle_status
        strJsonLineContent = json.dumps(dictLogInfo)

        try:
            folder_check()
            with open('/home/mogo/data/log/filebeat_upload/vehicle_status.log', 'a+') as f:
                f.write(strJsonLineContent)
                f.write("\n")

        except Exception as e:
            rospy.logwarn("operate file failed")
            rospy.logwarn('repr(e):\t', repr(e))
            rospy.logwarn('e.message:\t', e.message)
            rospy.logwarn('traceback.format_exc():\n%s' % (traceback.format_exc()))


def autopilotModeCallback(msg):

    pbStatus=common_vehicle_state_pb2.VehicleState()
    pbStatus.ParseFromString(msg.data)



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

    if msg.size > 0:
        globalVihiclePool.submit(task_vehicle,msg.data)



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

def decisionStateCallback(msg):
    pass

def addLocalizationListener():
    rospy.Subscriber('/localization/global', BinaryData, localizationCallback)
    rospy.Subscriber('/chassis/vehicle_state', BinaryData, autopilotModeCallback)
    rospy.Subscriber('/planning/decision_state',BinaryData,decisionStateCallback)

def main():
    # initial node
    globalCommonPara.initPara()
    rospy.init_node('monitor_gnss', anonymous=True)
    # add listener
    global globalWriteInterval
    strFullParaName = "%s/monitor_gnss_interval" %(rospy.get_name())
    rospy.loginfo("strFullParaName:%s" %(strFullParaName))
    temp  = rospy.get_param(strFullParaName)
    if temp  >= 1000 or temp <= 0 :
        globalWriteInterval =  1000
    else:
        globalWriteInterval =  temp
    rospy.loginfo("=============================set globalWriteInterval:%d" %(globalWriteInterval))
    addLocalizationListener()
    ## wait msg
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        rospy.logwarn("monitor.py is failed !")
        exit(0)
