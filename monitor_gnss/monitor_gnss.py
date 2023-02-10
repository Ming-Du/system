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
import common.localization_pb2 as common_localization
import common.vehicle_state_pb2 as common_vehicle_state_pb2
from  entity.LocInfo import  LocInfo
from entity.CommonPara import  CommonPara
import common.message_pad_pb2 as common_message_pad
import common.system_state_report_pb2 as common_system_state_report
import common.trfclts_statistics_pb2 as common_trfclts_statistics
import common.telematics_statistics_pb2 as common_telematics_statistics

from threading import Thread
import threading
from concurrent.futures import ThreadPoolExecutor
import json
from entity.CollectVehicleInfo import   CollectVehicleInfo


# globalLocationPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_Location')
# globalVihiclePool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_vehicle')
# globalPlanningDecisionStatePool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_planningDecisionState')
# globalStateReportPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_StateReport')
# globalTrfcltsCtrlPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread_TrfcltsCtrl')
tree = lambda: collections.defaultdict(tree)
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

globalLastMicroSec_sys_state_report = 0
globalListSystem_state_report = []
globalWriteInterval_sys_state_report = 50

globalLastMicroSec_trfclts_ctrl = 0
globalListTrfclts_ctrl = []
globalWriteInterval_trfclts_ctrl = 50

globalLastMicroSec_tele_stat = 0

def folder_check():
    PATH='/home/mogo/data/log/filebeat_upload/'
    if os.path.isdir(PATH) and access(PATH, R_OK):
        pass
    else:
        rospy.logwarn("folder not ready,now create path")
        os.makedirs(PATH)
        os.chmod(PATH,0777)


def task_localization(pb_msg):
    location = common_localization.Localization()
    location.ParseFromString(pb_msg)

    dictPostionLog = {}
    dictPostionLog["pilotMode"] = int(globalCollectVehicleInfo.int_pilot_mode)
    dictPostionLog["takeover_reason_code"] = int(globalCollectVehicleInfo.int_error_code)
    dictPostionLog["takeover_reason_message"] = str(globalCollectVehicleInfo.str_err_msg)
    dictPostionLog["position_x"] = location.position.x
    dictPostionLog["position_y"] = location.position.y
    dictPostionLog["location_longitude"] = location.longitude
    dictPostionLog["location_latitude"] = location.latitude

    dictPostionLog["roll"] = location.roll
    dictPostionLog["pitch"] = location.pitch
    dictPostionLog["yaw"] = location.yaw
    dictPostionLog["roll_v"] = location.roll_v
    dictPostionLog["pitch_v"] = location.pitch_v
    dictPostionLog["yaw_v"] = location.yaw_v
    dictPostionLog["lateral_v"] = location.lateral_v
    dictPostionLog["longitudinal_v"] = location.longitudinal_v
    dictPostionLog["vertical_v"] = location.vertical_v
    dictPostionLog["lateral_a"] = location.lateral_a
    dictPostionLog["longitudinal_a"] = location.longitudinal_a

    dictPostionLog["vertical_a"] = location.vertical_a
    dictPostionLog["horizontal_v"] = location.horizontal_v
    dictPostionLog["utm_zone"] = location.utm_zone
    dictPostionLog["gnss_sys_dtime"] = location.gnss_sys_dtime
    dictPostionLog["rtk_counts"] = location.gnss_num
    dictPostionLog["altitude"] = location.altitude

    CurrentMicroSec = location.header.stamp.sec * 1000 + location.header.stamp.nsec / 1000000
    dictPostionLog["msec"] = CurrentMicroSec

    global globalListPostion
    global globalLastMicroSec

    globalListPostion.append(dictPostionLog)

    if len(globalListPostion) >= 1000 / globalWriteInterval:
        dictLogInfo = tree()
        dictLogInfo["log_type"] = "location"
        dictLogInfo["timestamp"]['sec'] = rospy.rostime.Time.now().secs
        dictLogInfo["timestamp"]["nsec"] = rospy.rostime.Time.now().nsecs
        dictLogInfo["car_info"] = globalCommonPara.dictCarInfo
        dictLogInfo["positions"] = globalListPostion
        strJsonLineContent = json.dumps(dictLogInfo)

        try:

            with open('/home/mogo/data/log/filebeat_upload/location.log', 'a+') as f:
                f.write(strJsonLineContent)
                f.write("\n")
            globalListPostion = []
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))



def localizationCallback(msg):
    global globalLastMicroSec
    sec = rospy.rostime.Time.now().secs
    nsec = rospy.rostime.Time.now().nsecs
    CurrentMicroSec = sec * 1000 + nsec / 1000000
    if CurrentMicroSec - globalLastMicroSec >= globalWriteInterval:
        if msg.size > 0:
            task_localization(msg.data)
            globalLastMicroSec = CurrentMicroSec

def task_vehicle(pb_msg):
    pbStatus = common_vehicle_state_pb2.VehicleState()
    pbStatus.ParseFromString(pb_msg.data)

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
        # hxy added these 2 fields at 20221208
        dictVehicleLog['bms_soc'] = pbStatus.bms_soc
        dictVehicleLog['fuel_value'] = pbStatus.fuel_value

    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    sec = pb_msg.header.stamp.secs
    nsec = pb_msg.header.stamp.nsecs

    CurrentMicroSec = sec*1000 + nsec/1000000
    dictVehicleLog['sec'] = sec
    dictVehicleLog['nsec'] = nsec
    dictVehicleLog["msec"] = CurrentMicroSec

    global globalListPostion_vehicle_status

    globalListPostion_vehicle_status.append(dictVehicleLog)

    if len(globalListPostion_vehicle_status) >= 1000 / globalWriteInterval_vehicle_status:
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
            with open('/home/mogo/data/log/filebeat_upload/vehicle_status.log', 'a+') as f:
                f.write(strJsonLineContent)
                f.write("\n")
            globalListPostion_vehicle_status = []

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def autopilotModeCallback(msg):
    global globalLastMicroSec_vehicle_status
    sec = rospy.rostime.Time.now().secs
    nsec = rospy.rostime.Time.now().nsecs
    CurrentMicroSec = sec * 1000 + nsec / 1000000
    if CurrentMicroSec - globalLastMicroSec_vehicle_status >= globalWriteInterval_vehicle_status:
        if msg.size > 0:
            task_vehicle(msg)
            globalLastMicroSec_vehicle_status = CurrentMicroSec




def task_stateReport(pb_msg):

    pbStatus = common_system_state_report.StateReport()
    pbStatus.ParseFromString(pb_msg)

    dictStateReport = {}

    dictStateReport['src'] = pbStatus.src
    dictStateReport['state'] = pbStatus.state
    dictStateReport['code'] = pbStatus.code
    dictStateReport['desc'] = pbStatus.desc
    dictStateReport['reserved'] = pbStatus.reserved

    sec = (pbStatus.header.stamp.sec)
    nsec = (pbStatus.header.stamp.nsec)

    CurrentMicroSec = sec * 1000 + nsec / 1000000
    dictStateReport['sec'] = sec
    dictStateReport['nsec'] = nsec
    dictStateReport["msec"] = CurrentMicroSec

    global globalListSystem_state_report
    global globalLastMicroSec_sys_state_report

    if CurrentMicroSec - globalLastMicroSec_sys_state_report >= 0:
        # rospy.logdebug_throttle(5, "enter first update globalLastMicroSec")
        globalListSystem_state_report.append(dictStateReport)
        ### update  last micro sec
        globalLastMicroSec_sys_state_report = CurrentMicroSec


    if len(globalListSystem_state_report) >= (1000 / globalWriteInterval_sys_state_report):
        dictLogInfo = tree()
        dictLogInfo["log_type"] = "sys_state_report"
        curSec = rospy.rostime.Time.now().secs
        curNsec = rospy.rostime.Time.now().nsecs
        dictLogInfo["timestamp"]['sec'] = curSec
        dictLogInfo["timestamp"]["nsec"] = curNsec
        dictLogInfo["car_info"] = globalCommonPara.dictCarInfo
        dictLogInfo["content"] = globalListSystem_state_report
        strJsonLineContent = json.dumps(dictLogInfo)

        try:
            with open('/home/mogo/data/log/filebeat_upload/system_state_report.log', 'a+') as f:
                f.write(strJsonLineContent)
                f.write("\n")
            globalListSystem_state_report = []
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def stateReportCallback(msg):
    # 本topic 频率低 不降频 多源无法控制时间间隔，所以不进行时间检查，直接进行转存
    if msg.size > 0:
        task_stateReport(msg.data)


def task_decisionState(pb_msg):
    pbStatus = common_message_pad.PlanningActionMsg()
    pbStatus.ParseFromString(pb_msg.data)

    dictDecisionState = {}
    dictDecisionState['driving_state']=pbStatus.action_msg.driving_state
    dictDecisionState['driving_action']=pbStatus.action_msg.driving_action
    dictDecisionState['destination_acc']=pbStatus.destination_acc



    sec = pb_msg.header.stamp.secs
    nsec = pb_msg.header.stamp.nsecs
    # rospy.logdebug("sec:{0},nsec:{1}".format(sec,nsec))

    CurrentMicroSec = sec * 1000 + nsec / 1000000
    dictDecisionState['sec'] = sec
    dictDecisionState['nsec'] = nsec
    dictDecisionState["msec"] = CurrentMicroSec

    global globalListPostion_decision_status
    global globalLastMicroSec_decision_status

    globalListPostion_decision_status.append(dictDecisionState)

    if len(globalListPostion_decision_status) >= 1000 / globalWriteInterval_decision_status:
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
            with open('/home/mogo/data/log/filebeat_upload/decision_status.log', 'a+') as f:
                f.write(strJsonLineContent)
                f.write("\n")
            globalListPostion_decision_status = []
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def decisionStateCallback(msg):
    global globalLastMicroSec_decision_status
    sec = rospy.rostime.Time.now().secs
    nsec = rospy.rostime.Time.now().nsecs
    CurrentMicroSec = sec * 1000 + nsec / 1000000
    if CurrentMicroSec - globalLastMicroSec_decision_status >= globalWriteInterval_decision_status:
        if msg.size > 0:
            task_decisionState(msg)
            globalLastMicroSec_decision_status = CurrentMicroSec


def task_trfcltsCtrl(pb_msg):
    pbStatus = common_trfclts_statistics.TrfcLtsStatistics()
    pbStatus.ParseFromString(pb_msg.data)
    dictTrfcltsCtrl = {}
    dictTrfcltsCtrl['cmd_cnt'] = pbStatus.cmd_cnt
    dictTrfcltsCtrl['obu_cnt'] = pbStatus.obu_cnt
    dictTrfcltsCtrl['v2n_cnt'] = pbStatus.v2n_cnt
    dictTrfcltsCtrl['hhp_cnt'] = pbStatus.hhp_cnt
    dictTrfcltsCtrl['shp_cnt'] = pbStatus.shp_cnt
    dictTrfcltsCtrl['vis_cnt'] = pbStatus.vis_cnt
    dictTrfcltsCtrl['log_cnt'] = pbStatus.log_cnt
    dictTrfcltsCtrl['cmd_ratio'] = round(pbStatus.cmd_ratio, 5) * 100
    dictTrfcltsCtrl['obu_ratio'] = round(pbStatus.obu_ratio, 5) * 100
    dictTrfcltsCtrl['v2n_ratio'] = round(pbStatus.v2n_ratio, 5) * 100
    dictTrfcltsCtrl['hhp_ratio'] = round(pbStatus.hhp_ratio, 5) * 100
    dictTrfcltsCtrl['shp_ratio'] = round(pbStatus.shp_ratio, 5) * 100
    dictTrfcltsCtrl['vis_ratio'] = round(pbStatus.vis_ratio, 5) * 100
    dictTrfcltsCtrl['log_ratio'] = round(pbStatus.log_ratio, 5) * 100

    global globalListTrfclts_ctrl
    globalListTrfclts_ctrl.append(dictTrfcltsCtrl)

    if len(globalListTrfclts_ctrl) >= (1000 / globalWriteInterval_trfclts_ctrl):
        dictLogInfo = tree()
        dictLogInfo["log_type"] = "trfclts_ctrl"
        curSec = rospy.rostime.Time.now().secs
        curNsec = rospy.rostime.Time.now().nsecs
        dictLogInfo["timestamp"]['sec'] = curSec
        dictLogInfo["timestamp"]["nsec"] = curNsec
        dictLogInfo["car_info"] = globalCommonPara.dictCarInfo
        dictLogInfo["content"] = globalListTrfclts_ctrl
        strJsonLineContent = json.dumps(dictLogInfo)

        try:
            with open('/home/mogo/data/log/filebeat_upload/trfclts_ctrl.log', 'a+') as f:
                f.write(strJsonLineContent)
                f.write("\n")
            globalListTrfclts_ctrl = []
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def trfcltsCtrlCallback(msg):
    global globalLastMicroSec_trfclts_ctrl
    sec = rospy.rostime.Time.now().secs
    nsec = rospy.rostime.Time.now().nsecs
    CurrentMicroSec = sec * 1000 + nsec / 1000000
    if CurrentMicroSec - globalLastMicroSec_trfclts_ctrl >= globalWriteInterval_trfclts_ctrl :
        if len(msg.data) > 0:
            task_trfcltsCtrl(msg)
            globalLastMicroSec_trfclts_ctrl = CurrentMicroSec


def task_teleStat(pb_msg):

    pbStatus = common_telematics_statistics.TelematicsStatistics()
    pbStatus.ParseFromString(pb_msg)

    dictTeleStat= dict()

    dictTeleStat['direction'] = pbStatus.direction
    dictTeleStat['target'] = pbStatus.target
    dictTeleStat['sessionID'] = pbStatus.sessionID
    dictTeleStat['statisticInterval'] = pbStatus.statisticInterval
    dictTeleStat['timestamp'] = pbStatus.timestamp
    dictTeleStat['items'] = dict()

    for key in pbStatus.items:
        dictTeleStat['items'][key] = dict()
        dictTeleStat['items'][key]['count'] = pbStatus.items.get(key).count
        dictTeleStat['items'][key]['hz'] = pbStatus.items.get(key).hz

        dictTeleStat['items'][key]['size'] = dict()
        dictTeleStat['items'][key]['size']['min'] = pbStatus.items.get(key).size.min
        dictTeleStat['items'][key]['size']['max'] = pbStatus.items.get(key).size.max
        dictTeleStat['items'][key]['size']['average'] = pbStatus.items.get(key).size.average

        dictTeleStat['items'][key]['timeCost'] = dict()
        dictTeleStat['items'][key]['timeCost']['min'] = pbStatus.items.get(key).timeCost.min
        dictTeleStat['items'][key]['timeCost']['max'] = pbStatus.items.get(key).timeCost.max
        dictTeleStat['items'][key]['timeCost']['average'] = pbStatus.items.get(key).timeCost.average


    global globalLastMicroSec_tele_stat

    if dictTeleStat['timestamp'] - globalLastMicroSec_tele_stat >= 0:
        globalLastMicroSec_tele_stat = dictTeleStat['timestamp']

        dictLogInfo = dict()
        dictLogInfo["log_type"] = "tele_stat"
        dictLogInfo["car_info"] = globalCommonPara.dictCarInfo
        dictLogInfo["content"] = dictTeleStat
        strJsonLineContent = json.dumps(dictLogInfo)


        try:
            with open('/home/mogo/data/log/filebeat_upload/tele_stat.log', 'a+') as f:
                f.write(strJsonLineContent)
                f.write("\n")
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def teleStatCallback(msg):
    if msg.size > 0:
        task_teleStat(msg.data)


def addLocalizationListener():
    rospy.Subscriber('/localization/global', BinaryData, localizationCallback)
    rospy.Subscriber('/chassis/vehicle_state', BinaryData, autopilotModeCallback)
    rospy.Subscriber('/planning/decision_state',BinaryData,decisionStateCallback)
    # huxinyu added this new topic at 20221206
    rospy.Subscriber('/system_master/StateReport', BinaryData, stateReportCallback)
    # huxinyu added this new topic at 20230104
    rospy.Subscriber('/perception/camera/trfclts_ctrl_statistics', String, trfcltsCtrlCallback)
    # huxinyu added this new topic at 20230202
    rospy.Subscriber('/telematics/statistics', BinaryData, teleStatCallback)


def main():
    # initial node
    globalCommonPara.initPara()
    rospy.init_node('monitor_gnss', anonymous=True)
    # add listener
    global globalWriteInterval
    global globalWriteInterval_vehicle_status
    global globalWriteInterval_decision_status
    global globalWriteInterval_sys_state_report
    global globalWriteInterval_trfclts_ctrl

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

    strFullParaName = "%s/monitor_gnss_interval_system_state_report" % (rospy.get_name())
    rospy.loginfo("strFullParaName:%s" % (strFullParaName))
    temp = rospy.get_param(strFullParaName)
    if temp >= 1000 or temp <= 0:
        globalWriteInterval_sys_state_report = 1000
    else:
        globalWriteInterval_sys_state_report = temp

    strFullParaName = "%s/monitor_gnss_interval_trfclts_ctrl" % (rospy.get_name())
    rospy.loginfo("strFullParaName:%s" % (strFullParaName))
    temp = rospy.get_param(strFullParaName)
    if temp >= 1000 or temp <= 0:
        globalWriteInterval_trfclts_ctrl = 1000
    else:
        globalWriteInterval_trfclts_ctrl = temp

    rospy.loginfo("set globalWriteInterval:{0},globalWriteInterval_vehicle_status:{1},globalWriteInterval_decision_status:{2},globalWriteInterval_sys_state_report:{3},globalWriteInterval_trfclts_ctrl:{4}".format(globalWriteInterval,globalWriteInterval_vehicle_status,globalWriteInterval_decision_status,globalWriteInterval_sys_state_report, globalWriteInterval_trfclts_ctrl))
    folder_check()
    addLocalizationListener()
    ## wait msg
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        rospy.logwarn("monitor.py is failed !")
        exit(0)
