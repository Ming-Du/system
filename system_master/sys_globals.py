#!/usr/bin/python2 
# -*- coding: utf-8 -*-
'''
Author: your name
Date: 2022-04-27 11:32:52
LastEditTime: 2022-05-12 09:40:08
LastEditors: liyuelei liyuelei@zhidaoauto.com
Description: the file used for globals and constants
FilePath: /catkin_ws/src/system/system_master/sys_globals.py
'''

from concurrent.futures import ThreadPoolExecutor

g_system_master_entity = None   # global entity
g_all_agent_list = dict()     # k=ip, v=Agent()
g_master_httpd_port = 8080
g_system_state_save_file = '/tmp/system_state'
g_system_master_state_report = '/home/mogo/data/log/msg_log/system_master_report.json'

g_SysMsgPool = ThreadPoolExecutor(max_workers=3, thread_name_prefix='globalSystemMsgPool')

class System_State():
    # system_state
    SYS_STARTING = 0
    SYS_RUNNING = 1
    SYS_EXITING = 2
    SYS_FAULT = 3
    # autopilot state
    AUTO_PILOT_READY = 4
    AUTO_PILOT_STARTING = 5
    AUTO_PILOT_RUNNING = 6
    # remote state
    REMOTE_PILOT_STARTING = 7
    REMOTE_PILOT_RUNNING = 8
    MANUAL_PILOT_STATE = 9

    # mogo_report msg 
    System_Report_Code = {
        # state: ['code','results','actions']
        0: ["ISYS_STARTING",['RESULT_AUTOPILOT_DISABLE', 'RESULT_REMOTEPILOT_DISABLE'],[]],
        1: ["ISYS_RUNNING",[],[]],
        2: ["ISYS_EXITING",['RESULT_AUTOPILOT_DISABLE', 'RESULT_REMOTEPILOT_DISABLE'],[]],
        3: ["ESYS_FAULT",['RESULT_AUTOPILOT_DISABLE','RESULT_REMOTEPILOT_DISABLE'],['ACTION_REBOOT_VEHICLE']],
        4: ["ISYS_AUTOPILOT_READY",[],[]],
        5: ["ISYS_AUTOPILOT_STARTING",[],[]],
        6: ["ISYS_AUTOPILOT_RUNING",[],[]],
        7: ["ISYS_REMOTEPILOT_STARTING",[],[]],
        8: ["ISYS_REMOTEPILOT_RUNING",[],[]]
    }

    #state change reason
    STATE_CHANGE_BY_AGENT = 0
    STATE_CHANGE_BY_AUTOPILOT_CMD = 1
    STATE_CHANGE_BY_REAL_VEHICLE_STATE = 2
    STATE_CHANGE_BY_SYS_REBOOT_CMD = 3
    STATE_CHANGE_BY_MOGO_EVENT = 4
    STATE_CHANGE_BY_TRAJECTORY_RESULT = 5

    Change_Reason = {
        0: 'agent_act',     # check agent all(True)
        1: 'autopilot_cmd',  # 1: start_auto pilot   0: stop autopilot  2: star remote pilot 
        2: 'vehicle_state', # 1: auto pilot already  0: auto pilot real exit  2:
        3: 'sys_reboot',  
        4: 'sys_event_msg', 
        5: 'download_Trajectory'  
    }


class Agent_State():
    AGENT_IS_INITING = 0
    AGENT_ROSCORE_RUN = 2
    AGENT_ROSCORE_DOWN = 4
    AGENT_NODES_WORKED = 6
    AGENT_NODE_PART_WORKED = 7
    AGENT_NODES_STOPPED = 9

    State_Desc = {
        0: 'initing',
        1: 'roscore starting',
        2: 'roscore started',
        3: 'roscore stopping',
        4: 'roscore stopped',
        5: 'node starting',
        6: 'all nodes working',
        7: 'partial nodes working',
        8: 'node stopping',
        9: 'all nodes shutdown',
    }


class SysCmd_to_Agent():
    g_agent_mogo_pwd = 'CC8775c0fe94'
    Get_Agent_Pid = 'ssh -p 2222 -l mogo {} -o StrictHostKeyChecking=no ps -ef | grep -w "autopilot.sh" |grep -v grep' # need ip 
    Xavier_On = 'ssh -p 2222 -l mogo {} sudo kill -10 {}'  # need ip, pid
    Xavier_Off = 'ssh -p 2222 -l mogo {} sudo kill -12 {}'  # need ip, pid
    Get_MAP_Version = 'ssh -p 2222 -l mogo 127.0.0.1 -o StrictHostKeyChecking=no "head -n 3 /autocar-code/project_commit.txt"'


class System_Msg_Report():
    SYSTEM_MASTER_PB_DEF_FILE = 'mogo_master.pb'

    Error_Report_Code = {
        #code: ['msg','results','actions']
        'EHW_CAN': ['can adapter pub msg lost',['RESULT_AUTOPILOT_DISABLE'],['ACTION_REBOOT_VEHICLE']],
        'ESYS_AUTOPILOT_FAILED': ['autopilot start timeout',['RESULT_AUTOPILOT_DISABLE','RESULT_AUTOPILOT_INFERIOR'],['ACTION_TRY_AGAIN_LATER','ACTION_CONTACT_TECH_SUPPORT']],
        'ESYS_REMOTEPILOT_FAILED': ['remotepilot start timeout',['RESULT_REMOTEPILOT_DISABLE'],['ACTION_CONTACT_TECH_SUPPORT']],
        'ESYS_IN_INIT': ['state not allow autopilot',['RESULT_AUTOPILOT_DISABLE'],['ACTION_TRY_AGAIN_LATER']],
        'ESYS_IN_EXIT': ['state not allow autopilot',['RESULT_AUTOPILOT_DISABLE'],[]],
        'ESYS_NOT_ALLOW_AUTOPILOT_FOR_REMOTE': ['state not allow autopilot',['RESULT_AUTOPILOT_DISABLE'],[]],
        'ESYS_NOT_ALLOW_REMOTEPILOT': ['state not allow remotepilot',['RESULT_REMOTEPILOT_DISABLE'],['ACTION_CONTACT_TECH_SUPPORT']],
        'ESYS_NOT_ALLOW_REBOOT': ['state not allow sysreboot',[],['ACTION_TRY_AGAIN_LATER']],
        'ESYS_TOPIC_FREQ_DROPED': ['some topic frequency droped',['RESULT_AUTOPILOT_INFERIOR'],[]],
        'ESYS_RTK_STATUS_FAULT': ['rtk status is unexpected',['RESULT_AUTOPILOT_INFERIOR'],[]],
        'ELCT_RTK_STATUS_FAULT': ['rtk status is error',['RESULT_AUTOPILOT_DISABLE'],[]],
        'ELCT_RTK_STATUS_UNKNOWN': ['rtk status is unkonw',['RESULT_SHOW_WARNING'],[]],
        'ESYS_ROUTING_REQ_TIMEOUT': ['routing request timeout',['RESULT_AUTOPILOT_DISABLE'],['ACTION_TRY_AGAIN_LATER']],
        'ESYS_AUTOPILOT_TAKEN_OVER_BY_REMOTE': ['autopilot is takeover by remote',['RESULT_AUTOPILOT_DISABLE'],[]]
    }

    Info_Report_Code = {
        'ISYS_CAN_NORMAL':['can adapter pub msg normal',[],[]],
        'ISYS_TOPIC_FREQ_NORMAL': ['all topic frequency normal',[],[]],
        'ISYS_INIT_TRAJECTORY_START': ['start trajectory download',[],[]],
        'ISYS_INIT_TRAJECTORY_TIMEOUT': ['trajectory download timeout',[],[]],
        'ISYS_INIT_TRAJECTORY_SUCCESS': ['trajectory download success',[],[]],
        'ISYS_INIT_TRAJECTORY_FAILURE': ['trajectory download failed',[],[]],
        'ISYS_INIT_TRAJECTORY_WARNING': ['trajectory download failed, but used local file',[],[]],
        'ILCT_RTK_STATUS_NORMAL': ['rtk status is normal',[],[]], ## used in MAP_V250
        'ISYS_RTK_STATUS_NORMAL': ['rtk status is effective',[],[]]  ## used in MAP_V240
    }


class Sys_Health_Check():
    g_rtk_last_timestamp = 0
    g_rtk_had_send_error = False

    g_topic_hz_error_dict = dict()
    g_topic_hz_send_error = False

    g_can_adapter_last_recvtime = 0
    g_can_adapter_had_send_error = False

    g_health_status_dict = {
        #node : [state,code,desc]
        "localization":{
            'state': 0,
            'code': 'ISYS_RTK_STATUS_NORMAL',
            'desc': 'rtk state check'},
        "can_adapter":{
            'state': 0,
            'code': 'ISYS_CAN_NORMAL',
            'desc': 'can_adapter msg drop check'}
    }   


