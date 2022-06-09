#!/usr/bin/env python
# coding=utf-8
"""
#@Author: Orange
#@Date: 2022-05-16 09:57:08
#@FilePath: /catkin_ws/src/system/system_master/sys_config.py
#@Email: liyuelei@zhidaoauto.com
#@LastEditTime: 2022-06-08 21:21:03
"""


SYSTRM_MASTER_VERSION = "MAP-V2.5.0(MASTER-V1.0.4)"

g_local_test_flag = False  # if local test, not in car, can set it Ture

g_get_report_msg_config_by_pb = True  # if true used master.pb form mogo_reporter

TRAJECTORY_DOWNLOAD_WAIT_TIME = 30 #sec

ALL_AGENT_WORKED_WAIT_TIME = 10*60 #sec

REMOTE_POLIT_START_WAIT_TIME = 6  #sec

AUTO_POLIT_START_WAIT_TIME = 3   # sec   HQ|DF: need 5 sec  BUS: need 2 sec, system larger than them

HEARTBEAT_TIMEOUT_OF_AGENT = 5   # sec

CAN_PUB_MSG_LSOT_MAX_TIME = 2    # sec

RTK_STATUS_EFFECTIVE_RERIOD = 8  # sec

TOPIC_HZ_DROP_THRESHOLD = 0.6    # 80%

Minitor_Topic_Dict = {
    # topic_name: freq
    "/sensor/gnss/imu": 100,
    # "/sensor/gnss/best_gnss_vel": 100,
    "/sensor/gnss/gps_fix": 100,
    # '/sensor/gnss/odometry': 100,
    #'/sensor/gnss/reference_time': 100,
    #'/sensor/camera/sensing/image_raw_60/nvjpeg': 20,
    '/localization/global': 100,
    #'/guardian/aicloud_state': 2,
    '/planning/trajectory': 10,
    #'/planning/leader': 10,
    '/chassis/command': 100,
    '/telematics/light': 2,
    '/hadmap_engine/map_msg': 10,
    '/hadmap_engine/lanes_msg': 10,
    '/perception/camera/camera_obstacle': 20,
    '/perception/lidar/lidar_obstacle': 10
    #'/perception/camera/trfclts_state': 20,
    #'/chassis/vehicle_state': 50,
    #'/prediction/PredictionObstacles': 9  
}

Sys_Handle_Event_Code = {
    "EINIT_UPDATE": 1,
    "EINIT_BOOT": 2,
    "EHW_LIDAR": 3,
    "EHW_GNSS": 4,
    "EHW_CAN": 5,
    "EHW_NET": 6,
    "EMAP_NODE": 7,
    "EMAP_TOPIC":8,
    "EMAP_TRA":9,
    "EVHC_GEAR":10,
    "EVHC_CSS":11
}



