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
import proto.message_pad_pb2 as common_message_pad

from threading import Thread
import threading
from concurrent.futures import ThreadPoolExecutor
import json
from entity.CollectVehicleInfo import   CollectVehicleInfo


globalLocationPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_Location')
globalVihiclePool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_vehicle')
globalPlanningDecisionStatePool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_planningDecisionState')
globalCollectVehicleInfo  = CollectVehicleInfo()
globalCommonPara = CommonPara()
globalLastMicroSec = 0
globalListPostion = []
globalWriteInterval = 50


globalLastMicroSec_vehicle_status = 0
globalListPostion_vehicle_status = []
globalWriteInterval_vehicle_status = 50


globalLastMicroSec_decision_status = 0
globalListPostion_decision_status = []
globalWriteInterval_decision_status = 50

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
    rospy.logdebug("instanceLocInfoUnit.MarkMapPosition_x:{0}".format(instanceLocInfoUnit.MarkMapPosition_x))
    instanceLocInfoUnit.MarkMapPosition_y = location.position.y
    rospy.logdebug("instanceLocInfoUnit.MarkMapPosition_y:{0}".format(instanceLocInfoUnit.MarkMapPosition_y))
    instanceLocInfoUnit.MarkMapPosition_longitude = location.longitude
    rospy.logdebug("instanceLocInfoUnit.MarkMapPosition_longitude:{0}".format(instanceLocInfoUnit.MarkMapPosition_longitude))
    instanceLocInfoUnit.MarkMapPosition_latitude = location.latitude
    rospy.logdebug("instanceLocInfoUnit.MarkMapPosition_latitude:{0}".format(instanceLocInfoUnit.MarkMapPosition_latitude))
    instanceLocInfoUnit.roll=location.roll
    rospy.logdebug("instanceLocInfoUnit.roll".format(instanceLocInfoUnit.roll))
    instanceLocInfoUnit.pitch=location.pitch
    rospy.logdebug("instanceLocInfoUnit.pitch:{0}".format(instanceLocInfoUnit.pitch))
    instanceLocInfoUnit.yaw=location.yaw
    rospy.logdebug("ineLocInfoUnit.yaw:{0}".format(instanceLocInfoUnit.yaw))
    instanceLocInfoUnit.roll_v=location.roll_v
    rospy.logdebug("instanceLocInfoUnit.roll_v:{0}".format(instanceLocInfoUnit.roll_v))
    instanceLocInfoUnit.pitch_v=location.pitch_v
    rospy.logdebug("instanceLocInfoUnit.pitch_v:{0}".format(instanceLocInfoUnit.pitch_v))
    instanceLocInfoUnit.yaw_v=location.yaw_v
    rospy.logdebug("instanceLocInfoUnit.yaw_v:{0}".format(instanceLocInfoUnit.yaw_v))
    instanceLocInfoUnit.lateral_v=location.lateral_v
    rospy.logdebug("instanceLocInfoUnit.lateral_v:{0}".format(instanceLocInfoUnit.lateral_v))
    instanceLocInfoUnit.longitudinal_v=location.longitudinal_v
    rospy.logdebug("instanceLocInfoUnit.longitudinal_v:{0}".format(instanceLocInfoUnit.longitudinal_v))
    instanceLocInfoUnit.vertical_v=location.vertical_v
    rospy.logdebug("instanceLocInfoUnit.vertical_v:{0}".format(instanceLocInfoUnit.vertical_v))
    instanceLocInfoUnit.lateral_a=location.lateral_a
    rospy.logdebug("instanceLocInfoUnit.lateral_a:{0}".format(instanceLocInfoUnit.lateral_a))
    instanceLocInfoUnit.longitudinal_a=location.longitudinal_a
    rospy.logdebug("instanceLocInfoUnit.longitudinal_a:{0}".format(instanceLocInfoUnit.longitudinal_a))
    instanceLocInfoUnit.vertical_a=location.vertical_a
    rospy.logdebug("instanceLocInfoUnit.vertical_a:{0}".format(instanceLocInfoUnit.vertical_a))
    instanceLocInfoUnit.horizontal_v=location.horizontal_v
    rospy.logdebug("instanceLocInfoUnit.horizontal_v:{0}".format(instanceLocInfoUnit.horizontal_v))
    instanceLocInfoUnit.utm_zone=location.utm_zone
    rospy.logdebug("instanceLocInfoUnit.utm_zone:{0}".format(instanceLocInfoUnit.utm_zone))
    instanceLocInfoUnit.gnss_sys_dtime=location.gnss_sys_dtime
    rospy.logdebug("instanceLocInfoUnit.gnss_sys_dtime:{0}".format(instanceLocInfoUnit.gnss_sys_dtime))
    instanceLocInfoUnit.sec =  (location.header.stamp.sec)
    rospy.logdebug("instanceLocInfoUnit.sec:{0}".format(instanceLocInfoUnit.sec))
    instanceLocInfoUnit.nsec = (location.header.stamp.nsec)
    rospy.logdebug("instanceLocInfoUnit.nsec:{0}".format(instanceLocInfoUnit.nsec))


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
            globalListPostion = []
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))



def localizationCallback(msg):
    if msg.size > 0:
        globalLocationPool.submit(task_localization, msg.data)

def task_vehicle(pb_msg):
    pbStatus = common_vehicle_state_pb2.VehicleState()
    pbStatus.ParseFromString(pb_msg)
    # instanceVehicleInfo = CollectVehicleInfo()
    # instanceVehicleInfo.int_pilot_mode = pbStatus.pilot_mode
    #rospy.logdebug("instanceVehicleInfo.int_pilot_mode:{0}".format(instanceVehicleInfo.int_pilot_mode))
    # instanceVehicleInfo.b_steer_inference = pbStatus.steer_inference
    # rospy.logdebug("instanceVehicleInfo.b_steer_inference:{0}".format(instanceVehicleInfo.b_steer_inference))
    # instanceVehicleInfo.b_brake_inference = pbStatus.brake_inference
    # rospy.logdebug("itanceVehicleInfo.b_brake_inference:{0}".format(instanceVehicleInfo.b_brake_inference))
    # instanceVehicleInfo.b_accel_inference = pbStatus.accel_inference
    # rospy.logdebug("instanceVehicleInfo.b_accel_inference:{0}".format(instanceVehicleInfo.b_accel_inference ))
    # instanceVehicleInfo.b_gear_switch_inference = pbStatus.gear_switch_inference
    # rospy.logdebug("instanceVehicleInfo.b_gear_switch_inference:{0}".format(instanceVehicleInfo.b_gear_switch_inference))
    # instanceVehicleInfo.b_location_missing = pbStatus.location_missing
    # rospy.logdebug("instanceVehicleInfo.b_location_missing:{0}".format(instanceVehicleInfo.b_location_missing))
    # instanceVehicleInfo.b_trajectory_missing = pbStatus.trajectory_missing
    # rospy.logdebug("instanceVehicleInfo.b_trajectory_missing:{0}".format(instanceVehicleInfo.b_trajectory_missing))
    # instanceVehicleInfo.b_chassis_status_missing = pbStatus.chassis_status_missing
    # rospy.logdebug("instanceVehicleInfo.b_chassis_status_missing:{0}".format(instanceVehicleInfo.b_chassis_status_missing ))
    # instanceVehicleInfo.brake_light_status = pbStatus.brake_light_status
    # rospy.logdebug("instanceVehicleInfo.brake_light_status:{0}".format(instanceVehicleInfo.brake_light_status))
    # #instanceVehicleInfo.pilot_mode_condition_met = pbStatus.pilot_mode_condition_met
    # #rospy.logdebug("instanceVehicleInfo.pilot_mode_condition_met:{0}".format(instanceVehicleInfo.pilot_mode_condition_met))
    # instanceVehicleInfo.steeringSpd = pbStatus.steeringSpds
    # rospy.logdebug("instanceVehicleInfo.steeringSpd:{0}".format(instanceVehicleInfo.steeringSpd))
    # instanceVehicleInfo.leftFrontWheelAngle = pbStatus.leftFrontWheelAngle
    # rospy.logdebug("instanceVehicleInfo.leftFrontWheelAngle:{0}".format(instanceVehicleInfo.leftFrontWheelAngle))
    # instanceVehicleInfo.rightFrontWheelAngle = pbStatus.rightFrontWheelAngle
    # rospy.logdebug("instanceVehicleInfo.rightFrontWheelAngle:{0}".format(instanceVehicleInfo.rightFrontWheelAngle))
    # instanceVehicleInfo.steering = pbStatus.steering
    # rospy.logdebug("instanceVehicleInfo.steering:{0}".format(instanceVehicleInfo.steering ))
    # instanceVehicleInfo.speed = pbStatus.speed
    # rospy.logdebug("instanceVehicleInfo.speed:{0}".format(instanceVehicleInfo.speed))
    # instanceVehicleInfo.accel = pbStatus.accel
    # rospy.logdebug("instanceVehicleInfo.accel:{0}".format(instanceVehicleInfo.accel))
    # instanceVehicleInfo.throttle = pbStatus.throttle
    # rospy.logdebug("instanceVehicleInfo.throttle:{0}".format(instanceVehicleInfo.throttle))
    # instanceVehicleInfo.brake = pbStatus.brake
    # rospy.logdebug("instanceVehicleInfo.brake:{0}".format(instanceVehicleInfo.brake))
    # instanceVehicleInfo.gear = pbStatus.gear
    # rospy.logdebug("instanceVehicleInfo.gear:{0}".format(instanceVehicleInfo.gear))
    # instanceVehicleInfo.light = pbStatus.light
    # rospy.logdebug("instanceVehicleInfo.light:{0}".format(instanceVehicleInfo.light))
    # instanceVehicleInfo.horn = pbStatus.horn
    # rospy.logdebug("instanceVehicleInfo.horn:{0}".format(instanceVehicleInfo.horn))
    # instanceVehicleInfo.highbeam = pbStatus.highbeam
    # rospy.logdebug("instanceVehicleInfo.highbeam:{0}".format(instanceVehicleInfo.highbeam))
    # instanceVehicleInfo.lowbeam = pbStatus.lowbeam
    # rospy.logdebug("instanceVehicleInfo.lowbeam:{0}".format(instanceVehicleInfo.lowbeam))
    # instanceVehicleInfo.foglight = pbStatus.foglight
    # rospy.logdebug("instanceVehicleInfo.foglight:{0}".format(instanceVehicleInfo.foglight))
    # instanceVehicleInfo.clearance_lamps = pbStatus.clearance_lamps
    # rospy.logdebug("instanceVehicleInfo.clearance_lamps:{0}".format(instanceVehicleInfo.clearance_lamps))
    # instanceVehicleInfo.warn_light = pbStatus.warn_light
    # rospy.logdebug("instanceVehicleInfo.warn_light:{0}".format(instanceVehicleInfo.warn_light))
    # instanceVehicleInfo.parking_brake = pbStatus.parking_brake
    # rospy.logdebug("instanceVehicleInfo.parking_brake:{0}".format(instanceVehicleInfo.parking_brake))
    # instanceVehicleInfo.longitude_driving_mode = pbStatus.longitude_driving_mode
    # rospy.logdebug("instanceVehicleInfo.longitude_driving_mode:{0}".format(instanceVehicleInfo.longitude_driving_mode))
    # instanceVehicleInfo.eps_steering_mode = pbStatus.eps_steering_mode
    # rospy.logdebug("instanceVehicleInfo.eps_steering_mode:{0}".format(instanceVehicleInfo.eps_steering_mode))
    # instanceVehicleInfo.steering_sign = pbStatus.steering_sign
    # rospy.logdebug("instanceVehicleInfo.steering_sign:{0}".format(instanceVehicleInfo.steering_sign))
    dictVehicleLog = {}
    try:
        dictVehicleLog['int_pilot_mode'] = pbStatus.pilot_mode
        dictVehicleLog['b_steer_inference'] = pbStatus.steer_inference
        dictVehicleLog['b_brake_inference'] = pbStatus.brake_inference
        dictVehicleLog['b_accel_inference'] = pbStatus.accel_inference
        dictVehicleLog['b_gear_switch_inference'] = pbStatus.gear_switch_inference
        dictVehicleLog['b_location_missing'] = pbStatus.location_missing
        dictVehicleLog['b_trajectory_missing'] = pbStatus.trajectory_missing
        dictVehicleLog['b_chassis_status_missing'] = pbStatus.chassis_status_missing
        dictVehicleLog['brake_light_status'] = pbStatus.brake_light_status
        dictVehicleLog['steeringSpd'] = float(pbStatus.steeringSpd)
        dictVehicleLog['leftFrontWheelAngle'] = float(pbStatus.leftFrontWheelAngle)
        dictVehicleLog['rightFrontWheelAngle'] = float(pbStatus.rightFrontWheelAngle)
        dictVehicleLog['pilot_mode_condition_met']=float(pbStatus.pilot_mode_condition_met)
        dictVehicleLog['steering'] = pbStatus.steering
        dictVehicleLog['speed'] = pbStatus.speed
        dictVehicleLog['accel'] = pbStatus.accel
        dictVehicleLog['throttle'] = pbStatus.throttle
        dictVehicleLog['brake'] = pbStatus.brake
        dictVehicleLog['gear'] = pbStatus.gear
        dictVehicleLog['light'] = pbStatus.light
        dictVehicleLog['horn'] = pbStatus.horn
        dictVehicleLog['highbeam'] = pbStatus.highbeam
        dictVehicleLog['lowbeam'] = pbStatus.lowbeam
        dictVehicleLog['foglight'] = pbStatus.foglight
        dictVehicleLog['clearance_lamps'] = pbStatus.clearance_lamps
        dictVehicleLog['warn_light'] = pbStatus.warn_light
        dictVehicleLog['parking_brake'] = pbStatus.parking_brake
        dictVehicleLog['longitude_driving_mode'] = pbStatus.longitude_driving_mode
        dictVehicleLog['eps_steering_mode'] = pbStatus.eps_steering_mode
        dictVehicleLog['steering_sign'] = pbStatus.steering_sign
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    
    sec = 0
    nsec = 0
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
            globalListPostion_vehicle_status = []

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


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

def task_decisionState(pb_msg):
    pbStatus = common_message_pad.PlanningActionMsg()
    pbStatus.ParseFromString(pb_msg)
    dictDecisionState = {}
    dictDecisionState['driving_state']=pbStatus.action_msg.driving_state
    dictDecisionState['driving_action']=pbStatus.action_msg.driving_action
    dictDecisionState['destination_acc']=pbStatus.destination_acc
    rospy.logdebug("dictDecisionState:{0}".format(dictDecisionState))

    sec = rospy.rostime.Time.now().secs
    nsec = rospy.rostime.Time.now().nsecs
    rospy.logdebug("sec:{0},nsec:{1}".format(sec,nsec))

    CurrentMicroSec = sec * 1000 + nsec / 1000000
    dictDecisionState['sec'] = sec
    dictDecisionState['nsec'] = nsec
    dictDecisionState["msec"] = CurrentMicroSec

    global globalListPostion_decision_status
    global globalLastMicroSec_decision_status

    while True:
        if globalLastMicroSec_decision_status == 0:
            rospy.logdebug_throttle(5, "enter first update globalLastMicroSec")
            globalListPostion_vehicle_status.append(dictDecisionState)
            ## update last micro sec
            globalLastMicroSec_decision_status = CurrentMicroSec
            break
        if (CurrentMicroSec - globalLastMicroSec_decision_status > globalWriteInterval_decision_status) or (
                CurrentMicroSec - globalLastMicroSec_decision_status == globalWriteInterval_decision_status):
            rospy.logdebug_throttle(5, "enter first update globalLastMicroSec")
            globalListPostion_decision_status.append(dictDecisionState)
            ### update  last micro sec
            globalLastMicroSec_decision_status = CurrentMicroSec
            break
        break

    if (len(globalListPostion_decision_status) > (1000 / globalWriteInterval_decision_status)) or (
            len(globalListPostion_decision_status) == (1000 / globalWriteInterval_decision_status)):
        tree = lambda: collections.defaultdict(tree)
        dictLogInfo = tree()
        dictLogInfo["log_type"] = "decision_state"
        curSec = rospy.rostime.Time.now().secs
        curNsec = rospy.rostime.Time.now().nsecs
        dictLogInfo["timestamp"]['sec'] = curSec
        dictLogInfo["timestamp"]["nsec"] = curNsec
        dictLogInfo["car_info"] = globalCommonPara.dictCarInfo
        dictLogInfo["content"] = globalListPostion_decision_status
        strJsonLineContent = json.dumps(dictLogInfo)

        try:
            folder_check()
            with open('/home/mogo/data/log/filebeat_upload/decision_status.log', 'a+') as f:
                f.write(strJsonLineContent)
                f.write("\n")
            globalListPostion_decision_status = []
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
pass

def decisionStateCallback(msg):
    if msg.size > 0:
        globalPlanningDecisionStatePool.submit(task_decisionState,msg.data)


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
    global globalWriteInterval_vehicle_status
    global globalWriteInterval_decision_status
    strFullParaName = "%s/monitor_gnss_interval" %(rospy.get_name())
    rospy.loginfo("strFullParaName:%s" %(strFullParaName))
    temp  = rospy.get_param(strFullParaName)
    if temp  >= 1000 or temp <= 0 :
        globalWriteInterval =  1000
    else:
        globalWriteInterval =  temp

    strFullParaName = "%s/monitor_gnss_interval_vehicle" % (rospy.get_name())
    rospy.loginfo("strFullParaName:%s" % (strFullParaName))
    temp = rospy.get_param(strFullParaName)
    if temp >= 1000 or temp <= 0:
        globalWriteInterval_vehicle_status = 1000
    else:
        globalWriteInterval_vehicle_status = temp

    strFullParaName = "%s/monitor_gnss_interval_decision_status" % (rospy.get_name())
    rospy.loginfo("strFullParaName:%s" % (strFullParaName))
    temp = rospy.get_param(strFullParaName)
    if temp >= 1000 or temp <= 0:
        globalWriteInterval_decision_status = 1000
    else:
        globalWriteInterval_decision_status = temp



    rospy.loginfo("set globalWriteInterval:{0},globalWriteInterval_vehicle_status:{1},globalWriteInterval_decision_status:{2}".format(globalWriteInterval,globalWriteInterval_vehicle_status,
                                                                                       globalWriteInterval_decision_status))
    addLocalizationListener()
    ## wait msg
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        rospy.logwarn("monitor.py is failed !")
        exit(0)
