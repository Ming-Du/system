#!/usr/bin/python2 
# -*- coding: utf-8 -*-
'''
Author: your name
Date: 2022-04-27 15:29:25
LastEditTime: 2022-05-19 14:14:11
LastEditors: liyuelei liyuelei@zhidaoauto.com
Description: this file create for get vehiche state from /chassis/vihecle_state
FilePath: /catkin_ws/src/system/system_master/sys_vehicle_state.py
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time

import rospy
from proto import common_vehicle_state, system_pilot_mode_pb2, system_cmd_pb2, common_mogo_report_msg, common_log_reslove, system_state_report_pb2
from autopilot_msgs.msg import BinaryData
from std_msgs.msg import Int32, UInt64
from sensor_msgs.msg import NavSatFix
from sys_globals import System_State, System_Msg_Report, Sys_Health_Check
import sys_globals, sys_config

from system_master.srv import StatusQuery, StatusQueryResponse


class Vehicle_State():
    """
    #@name: 
    #@msg: receive /chassis/vehicle_state, change local state, pub /system_master/SysVehicleState once/s
    #@param undefined
    #@return {*}
    """

    def __init__(self):
        self.last_change_time = int(time.time())
        self.local_vehicle_state = None
        self.sys_vehicle_state_sub = rospy.Subscriber("/chassis/vehicle_state", BinaryData, self.get_vehicle_state)
        self.sys_vehicle_state_pub = rospy.Publisher('/system_master/SysVehicleState', BinaryData, queue_size=10)

    def get_vehicle_state(self, ros_msg):
        src_vehicle_state = common_vehicle_state.VehicleState()
        src_vehicle_state.ParseFromString(ros_msg.data)
        cur_time = int(time.time())
        Sys_Health_Check.g_can_adapter_last_recvtime = cur_time
        if not self.local_vehicle_state:
            # first time recv and save vehicle_state 
            self.local_vehicle_state = src_vehicle_state
            sys_globals.g_system_master_entity.change_sys_state(reason=System_State.STATE_CHANGE_BY_REAL_VEHICLE_STATE, act=src_vehicle_state.pilot_mode)
            self.pub_vehicle_state()
        else:
            if self.local_vehicle_state.pilot_mode != src_vehicle_state.pilot_mode:
                # state change  pub topic as soon as quickly
                self.local_vehicle_state = src_vehicle_state
                sys_globals.g_system_master_entity.change_sys_state(reason=System_State.STATE_CHANGE_BY_REAL_VEHICLE_STATE, act=src_vehicle_state.pilot_mode)
                self.pub_vehicle_state()
            elif cur_time > self.last_change_time:
                # state not change pub once every seconds 
                self.local_vehicle_state = src_vehicle_state 
                self.pub_vehicle_state()

    def pub_vehicle_state(self):
        pub_msg_data = system_pilot_mode_pb2.SYSVehicleState()
        pub_msg_data.header.seq          = self.local_vehicle_state.header.seq
        pub_msg_data.header.stamp.sec    = self.local_vehicle_state.header.stamp.sec
        pub_msg_data.header.stamp.nsec   = self.local_vehicle_state.header.stamp.nsec
        pub_msg_data.header.frame_id     = self.local_vehicle_state.header.frame_id
        pub_msg_data.pilot_mode = self.local_vehicle_state.pilot_mode
        pub_msg_data.steer_inference = self.local_vehicle_state.steer_inference
        pub_msg_data.brake_inference = self.local_vehicle_state.brake_inference
        pub_msg_data.accel_inference = self.local_vehicle_state.accel_inference
        pub_msg_data.gear_switch_inference = self.local_vehicle_state.gear_switch_inference
        pub_msg_data.location_missing = self.local_vehicle_state.location_missing
        pub_msg_data.trajectory_missing = self.local_vehicle_state.trajectory_missing
        pub_msg_data.chassis_status_missing = self.local_vehicle_state.chassis_status_missing
        pub_msg_data.brake_light_status = self.local_vehicle_state.brake_light_status
        pub_msg_data.pilot_mode_condition_met = self.local_vehicle_state.pilot_mode_condition_met

        pub_msg_data_str = pub_msg_data.SerializeToString()
        sys_state_msg = BinaryData()
        sys_state_msg.header.seq          = 1
        sys_state_msg.header.stamp.secs   = rospy.rostime.Time.now().secs
        sys_state_msg.header.stamp.nsecs  = rospy.rostime.Time.now().nsecs
        sys_state_msg.header.frame_id     = "system_master_frame_id"
        sys_state_msg.name = "system_master.SYSVehicleState"
        sys_state_msg.size = len(pub_msg_data_str)
        sys_state_msg.data = pub_msg_data_str
        
        self.sys_vehicle_state_pub.publish(sys_state_msg)
        self.last_change_time = int(time.time())



class Report_Msg_Analyze():
    """
    #@name: 
    #@msg: receive report msg and handle some specific event 
    #@param undefined
    #@return {*}
    """

    def __init__(self):
        self.sys_msg_log_info_sub = rospy.Subscriber("/autopilot_info/report_msg_info", BinaryData, self.analyze_report_msg)
        self.sys_msg_log_error_sub = rospy.Subscriber("/autopilot_info/report_msg_error", BinaryData, self.analyze_report_msg)

    
    def analyze_report_msg(self, msg):
        print('receive report mag, msg info:')
        if msg.size > 0:
            sys_globals.g_SysMsgPool.submit(self.task_report_msg, msg)

    def task_report_msg(self, msg):
        try:
            pbRecvMsg = common_mogo_report_msg.MogoReportMessage()
            pbRecvMsg.ParseFromString(msg.data)

            print("\ttimestamp.sec:\t{}".format(pbRecvMsg.timestamp.sec))
            print("\ttimestamp.nsec:\t{}".format(pbRecvMsg.timestamp.nsec))
            print("\tpbRecvMsg.src:\t{}".format(pbRecvMsg.src))
            print("\tpbRecvMsg.level:\t{}".format(pbRecvMsg.level))
            print("\tpbRecvMsg.msg:\t{}".format(pbRecvMsg.msg))
            print("\tpbRecvMsg.code:\t{}".format(pbRecvMsg.code))

            listTempResult = list()
            listTempAction = list()
            for elemResult in pbRecvMsg.result:
                listTempResult.append(elemResult)
            print('\tpbRecvMsg.result:\t{}'.format(listTempResult))    
            for elemAction in pbRecvMsg.actions:
                listTempAction.append(elemAction)
            print('\tpbRecvMsg.action:\t{}'.format(listTempAction))

            if pbRecvMsg.code in sys_config.Sys_Handle_Event_Code:
                self.handle_event_defined()

        except Exception as e:
            print("Exception happend", e)
    
    def handle_event_defined(self):
        pass



class Node_Handler(object):
    """
    #@name: this is system_master's node handle class 
    #@msg: all pub/sub will in this class
    #@param undefined
    #@return {*}
    """
    
    def __init__(self):
        self.autopolit_cmd_pub_time = 0
        self.vehicle_state_entity = Vehicle_State()
        self.report_msg_entity = Report_Msg_Analyze()
        self.rtk_status_detection_sub = rospy.Subscriber('/sensor/gnss/gps_fix', NavSatFix, self.handle_rtk_status)
        self.system_state_report_sub = rospy.Subscriber('/system_master/StateReport', BinaryData, self.handle_state_report)
        self.topic_status_detection_sub = rospy.Subscriber("/autopilot_info/internal/report_topic_hz", BinaryData, self.handle_topic_hz_status)
        self.system_command_sub = rospy.Subscriber("/system_master/SystemCmd", BinaryData, self.handle_system_cmd)
        self.system_autopolit_cmd_pub = rospy.Publisher('/autopilot/AutoPilotCmd', Int32, queue_size=10)
        self.system_diagnose_cmd_pub = rospy.Publisher('/system_master/CheckCmd', UInt64, queue_size=5)
        #self.system_event_info_pub  = rospy.Publisher('/autopilot_info/report_msg_info', BinaryData, queue_size=50)
        #self.system_event_error_pub = rospy.Publisher('/autopilot_info/report_msg_error', BinaryData, queue_size=50)

        ## add service by liyl 20200601
        self.query_request_service = rospy.Service('query_master_status', StatusQuery, self.handle_status_query_req)
    
              
    def set_pilot_mode(self, Mode):
        """
        #@name: 
        #@msg: setparam PilotMode and publish /autopilot/AutoPilotCmd to /controller
        #@return {*}
        """

        print('publist /autopilot/AutoPilotCmd: {}'.format(Mode))
        rospy.set_param("/autopilot/PilotMode", Mode)
        pilotcmd = Int32()
        pilotcmd.data = Mode
        self.system_autopolit_cmd_pub.publish(pilotcmd)
        self.autopolit_cmd_pub_time = rospy.rostime.Time.now()


    def pub_system_diagnose_cmd(self):
        """
        #@name: 
        #@msg: publish /system_master/CheckCmd to /mogodoctor
        #@return {*}
        """

        print('publist /system_master/CheckCmd: {}'.format(self.autopolit_cmd_pub_time))
        checkcmd = UInt64()
        checkcmd.data = self.autopolit_cmd_pub_time.to_nsec()
        self.system_diagnose_cmd_pub.publish(checkcmd)

    
    def pub_system_state_msg(self, msg='', code='', results=list(), actions=list(), level='info'):
        """
        #@name: 
        #@msg: modify by liyl 20220526 send system_state not used topic, save to file
        #@return {*}
        """

        sys_globals.g_system_master_entity.save_system_event_to_report_file(msg, code, results, actions, level)
        '''  # if used topic 
        mogo_report_msg = common_mogo_report_msg.MogoReportMessage()
        mogo_report_msg.timestamp.sec = rospy.rostime.Time.now().secs
        mogo_report_msg.timestamp.nsec = rospy.rostime.Time.now().nsecs
        mogo_report_msg.src = 'system_master'
        mogo_report_msg.level = level
        mogo_report_msg.msg = msg
        mogo_report_msg.code = code
        if level == "error":
            for result in results:
                mogo_report_msg.result.append(result)
            for action in actions:
                mogo_report_msg.actions.append(action)
        else:
            mogo_report_msg.result.append("")
            mogo_report_msg.actions.append("")
        
        sys_pub_msg_str = mogo_report_msg.SerializeToString()
        binary_log_msg = BinaryData()

        binary_log_msg.header.seq         = 1
        binary_log_msg.header.stamp.secs   = rospy.rostime.Time.now().secs
        binary_log_msg.header.stamp.nsecs  = rospy.rostime.Time.now().nsecs
        binary_log_msg.header.frame_id    = "system_master_frame_id"
        binary_log_msg.name = "mogo_msg.MogoReportMessage"
        binary_log_msg.size = len(sys_pub_msg_str)
        binary_log_msg.data = sys_pub_msg_str
        #print(log_pub_msg_str)
        if mogo_report_msg.level == "info":
            self.system_event_info_pub.publish(binary_log_msg)
        else:
            self.system_event_error_pub.publish(binary_log_msg)
        '''

    def build_system_state_msg(self, old_state, state):
        if state in System_State.System_Report_Code:
            msg = 'system state changed, form {} to {}'.format(old_state, state)
            code = System_State.System_Report_Code[state][0]
            results = System_State.System_Report_Code[state][1]
            actions = System_State.System_Report_Code[state][2]
            self.pub_system_state_msg(msg, code, results, actions)

    def system_event_report(self, code, desc=''):
        if code in System_Msg_Report.Error_Report_Code:
            msg = System_Msg_Report.Error_Report_Code[code][0] + desc
            results = System_Msg_Report.Error_Report_Code[code][1]
            actions = System_Msg_Report.Error_Report_Code[code][2]
            self.pub_system_state_msg(msg, code, results, actions, level='error')
        elif code in System_Msg_Report.Info_Report_Code:
            msg = System_Msg_Report.Info_Report_Code[code][0] + desc
            self.pub_system_state_msg(msg, code, [], [], level='info')
        else:
            print('The code {} not in system error event report list'.format(code))

    def send_roscore_coredump_event(self):
        pass
        """
        roscore is shutdown, report system event, the version don't handle
        
        msg = 'roscore is shutdown'
        code = ''
        results = []
        actions = []
        self.pub_system_state_msg(msg, code, results, actions, level='error')
        """


    def handle_system_cmd(self, ros_msg):
        """
        #@name: 
        #@msg: callback for sub msg from /telematics_node
        #@return {*}
        """

        src_sys_cmd = system_cmd_pb2.SystemCmd()
        src_sys_cmd.ParseFromString(ros_msg.data)

        if src_sys_cmd.src == system_cmd_pb2.AutoPolit:
            if src_sys_cmd.action in (system_cmd_pb2.StartPilot, system_cmd_pb2.StopPilot):
                mode = 1 if src_sys_cmd.action == system_cmd_pb2.StartPilot else 0
                sys_globals.g_system_master_entity.change_sys_state(1, mode)

            elif src_sys_cmd.action is system_cmd_pb2.SysReboot:
                if sys_globals.g_system_master_entity.auto_polit_state == 1:
                    self.system_event_report(code='ESYS_NOT_ALLOW_REBOOT', desc=' autopilot is working')
                else:
                    sys_globals.g_system_master_entity.handle_system_reboot()
            elif src_sys_cmd.action in (system_cmd_pb2.BeginShowMode, system_cmd_pb2.EndShowMode):
                sys_globals.g_system_master_entity.show_mode_flag = True if src_sys_cmd.action == system_cmd_pb2.BeginShowMode else False
                print('Show mode is {}, recv action {}'.format(sys_globals.g_system_master_entity.show_mode_flag, src_sys_cmd.action))
            else:
                print('Error: The action is [{}] unexpect!'.format(src_sys_cmd.action))
        elif src_sys_cmd.src == system_cmd_pb2.RemotePilot:
            print('Please contact liyl, The function need build')

    def handle_topic_hz_status(self, ros_msg):
        """
        #@name: 
        #@msg: callback for sub msg from /log_reslove
        #@return {*}
        """
        
        topic_hz_msg = common_log_reslove.PubLogInfo()
        topic_hz_msg.ParseFromString(ros_msg.data)
        for one_topic in topic_hz_msg.topic_hz:
            if one_topic.name in sys_config.Minitor_Topic_Dict:
                if one_topic.hz < (sys_config.Minitor_Topic_Dict[one_topic.name] * sys_config.TOPIC_HZ_DROP_THRESHOLD):
                    Sys_Health_Check.g_topic_hz_error_dict[one_topic.name] = one_topic.hz
                else:
                    if one_topic.name in Sys_Health_Check.g_topic_hz_error_dict:
                        del Sys_Health_Check.g_topic_hz_error_dict[one_topic.name]
        
        if len(Sys_Health_Check.g_topic_hz_error_dict):
            if not Sys_Health_Check.g_topic_hz_send_error:
                msg_desc=' topic and hz: {}'.format(Sys_Health_Check.g_topic_hz_error_dict)
                print('Error Topic' + msg_desc)
                self.system_event_report(code='ESYS_TOPIC_FREQ_DROPED', desc=msg_desc)
                Sys_Health_Check.g_topic_hz_send_error = True
        else:
            if Sys_Health_Check.g_topic_hz_send_error:
                self.system_event_report(code='ISYS_TOPIC_FREQ_NORMAL')
                Sys_Health_Check.g_topic_hz_send_error = False


    def handle_rtk_status(self, ros_msg):
        """
        #@name: 
        #@msg: callback for sub msg from /sensor/gnss/drivers_gnss
        #@return {*}
        """
        
        Status=ros_msg.status.status
        if Status != 42:
            cur_time = time.time()
            if not Sys_Health_Check.g_rtk_had_send_error and cur_time - Sys_Health_Check.g_rtk_last_timestamp > sys_config.RTK_STATUS_EFFECTIVE_RERIOD:
                msg_desc=' rtk status is {}'.format(Status)
                print('Error RTK:' + msg_desc)
                self.system_event_report(code='ESYS_RTK_STATUS_FAULT', desc=msg_desc)
                Sys_Health_Check.g_rtk_had_send_error = True
                
        else:
            Sys_Health_Check.g_rtk_last_timestamp = time.time()
            if Sys_Health_Check.g_rtk_had_send_error:
                self.system_event_report(code='ISYS_RTK_STATUS_NORMAL')
                Sys_Health_Check.g_rtk_had_send_error = False


    def check_can_adapter_pub_msg(self):
        """
        #@name: 
        #@msg: the function used for check can_adapter pub msg lost
        #@return {*}
        """
        cur_time = time.time()
        if cur_time - Sys_Health_Check.g_can_adapter_last_recvtime > sys_config.CAN_PUB_MSG_LSOT_MAX_TIME:
            if not Sys_Health_Check.g_can_adapter_had_send_error:
                msg_desc=' timestamp:{}'.format(cur_time)
                self.system_event_report(code='EHW_CAN', desc=msg_desc)
                Sys_Health_Check.g_can_adapter_had_send_error = True
        else:
            if Sys_Health_Check.g_can_adapter_had_send_error:
                msg_desc=' timestamp:{}'.format(cur_time)
                self.system_event_report(code='ISYS_CAN_NORMAL', desc=msg_desc)
                Sys_Health_Check.g_can_adapter_had_send_error = False

    def handle_state_report(self, ros_msg):
        state_report_msg = system_state_report_pb2.PubLogInfo()
        state_report_msg.ParseFromString(ros_msg.data)

        if 'localization' == state_report_msg.src:
            if state_report_msg.state in (state_report_msg.STATE_NORMAL, state_report_msg.STATE_FAULT, state_report_msg.STATE_UNKNOW):
                if state_report_msg.state != Sys_Health_Check.g_rtk_state_report_val:
                    print('rtk status change form {} to {}'.format(Sys_Health_Check.g_rtk_state_report_val, state_report_msg.state))
                    self.system_event_report(code=state_report_msg.code, desc=' '+state_report_msg.desc)
                    Sys_Health_Check.g_rtk_state_report_val = state_report_msg.state
            else:
                print('the state is unexpect! ignored! state={}'.format(state_report_msg.state))
        else:
            print('the src is unexpect! ignored! src={}'.format(state_report_msg.src))


    def handle_status_query_req(self, req):
		pass


    def run(self):
        # rospy.init_node('system_master', disable_signals=True)
        Sys_Health_Check.g_can_adapter_last_recvtime = time.time()
        rospy.spin()

    