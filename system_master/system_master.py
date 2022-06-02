#!/usr/bin/python2 
# -*- coding: utf-8 -*-

'''
Author: liyuelei
Date: 2022-04-26 18:33:56
LastEditTime: 2022-05-18 12:45:03
LastEditors: liyuelei liyuelei@zhidaoauto.com
Description: system master main loop
FilePath: /catkin_ws/src/system/system_master/system_master.py
'''

import sys
import os
import time
import json
import threading

###### ros module
import rospy

##### used master.pb from mogo_reporter
sys.path.append('../mogo_reporter/script')
from get_msg_by_code import gen_report_msg

#import local file
import sys_globals, sys_config
from sys_node_handler import Node_Handler
from sys_agent_handler import Agent_Handler
from sys_common import thread_with_trace



class System_Master(object):
    def __init__(self):
        self.state_file = sys_globals.g_system_state_save_file
        self.sys_state = -1  # default state
        self.auto_polit_state = -1
        self.show_mode_flag = False
        self.system_reboot_flag = False
        self.agent_handler_entity = Agent_Handler()
        self.node_handler_entity = None
        self.node_spin_thread = None
        self.auto_polit_wait_thread = None
        self.get_sys_state_before()

    def get_sys_state_before(self):
        '''
        get state from save_file
        '''
        state = -1
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as fp:
                st = fp.read().strip()
                print('Get old state from file is {}'.format(st))
                state = int(st)
        if state == -1:
            self.set_sys_state_and_save(sys_globals.System_State.SYS_STARTING)
        else:
            self.sys_state = state

    def set_sys_state_and_save(self, new_state):
        """
        #@name: 
        #@msg: call report msg function and save state
        #@return {*}
        """

        if self.sys_state != new_state:
            if new_state in sys_globals.System_State.System_Report_Code:
                msg = 'system state changed, form {} to {}'.format(self.sys_state, new_state)
                code = sys_globals.System_State.System_Report_Code[new_state][0]
                results = sys_globals.System_State.System_Report_Code[new_state][1]
                actions = sys_globals.System_State.System_Report_Code[new_state][2]
                self.save_system_event_to_report_file(msg, code, results, actions)
            ''' if used topic send
            if self.node_handler_entity and self.node_spin_thread.isAlive():
                self.node_handler_entity.build_system_state_msg(self.sys_state, new_state)
            '''
            self.sys_state = new_state
            with open(self.state_file, 'w+') as fp:
                fp.write(str(new_state))

    def save_system_event_to_report_file(self, msg='', code='', results=list(), actions=list(), level='info'):
        # system_report msg save to msg_log
        '''
        for Example :
        {"timestamp": {"sec": 1652260677, "nsec": 422577188}, 
        "src": "/home/mogo/catkin_ws/src/system/launch/autopilot.sh", 
        "action": ["ACTION_CONTACT_TECH_SUPPORT", "ACTION_CONTACT_MAINTENANCE"], 
        "code": "EVHC_TYPE_UNDEFINED", "result": ["RESULT_AUTOPILOT_SYSTEM_UNSTARTED", "RESULT_AUTOPILOT_DISABLE"], 
        "level": "error", "msg": "vehicle type undefined"}
        '''
        json_msg = '{}'
        if sys_config.g_get_report_msg_config_by_pb:
            try:
                json_msg = gen_report_msg(sys_globals.System_Msg_Report.SYSTEM_MASTER_PB_DEF_FILE, code)
            except Exception as e:
                print('Error: gen report msg failed!, {}'.format(e))

        if json_msg == '{}':  # if not used pb or call function error, used local config
            cur_time = int(time.time())
            msg_dict = {
                "timestamp": {
                    "sec": cur_time, 
                    "nsec": int((time.time() - cur_time) * 1000000000)}, 
                "src": "system_master", 
                "code": code, 
                "level": level, 
                "result": results,
                "action": actions,
                "msg": msg
            }
            json_msg = json.dumps(msg_dict)

        try:
            with open(sys_globals.g_system_master_state_report, 'a+') as fp:
                fp.write(json_msg +'\n')
        except Exception as e:
            print('Error: save report msg to file, {}'.format(e))

    def check_sys_state(self, autopilot_act):
        '''
        if sys_state is AUTO_PILOT_READY, system is RUNMNING, Autopilot can start, return True
        '''
        if autopilot_act and self.sys_state == sys_globals.System_State.AUTO_PILOT_READY:
            return True
        if not autopilot_act and self.sys_state == sys_globals.System_State.AUTO_PILOT_RUNNING:
            return True
        return False

    def change_sys_state(self, reason, act):
        '''
        change system state
        '''
        if reason not in sys_globals.System_State.Change_Reason:
            print('the reason is error!')
            return

        if reason == sys_globals.System_State.STATE_CHANGE_BY_AGENT:  # agent state
            if act == sys_globals.Agent_State.AGENT_NODES_WORKED: # all agent work
                self.set_sys_state_and_save(sys_globals.System_State.SYS_RUNNING)
                if self.node_spin_thread and self.node_spin_thread.isAlive():
                    self.set_sys_state_and_save(sys_globals.System_State.AUTO_PILOT_READY)
            else:
                print('the act {} is unexpected!'.format(act))

        elif reason == sys_globals.System_State.STATE_CHANGE_BY_AUTOPILOT_CMD: # auto cmd
            if self.check_sys_state(act):
                self.node_handler_entity.set_pilot_mode(act)
                if act == 1:
                    self.set_sys_state_and_save(sys_globals.System_State.AUTO_PILOT_STARTING)
                    self.auto_polit_wait_thread = threading.Timer(sys_config.AUTO_POLIT_START_WAIT_TIME, self.wait_autopolit_succ)
                    self.auto_polit_wait_thread.start()
            else:
                if act==1 and self.sys_state == sys_globals.System_State.SYS_STARTING:
                    self.node_handler_entity.system_event_report(code='ESYS_IN_INIT', desc=', system is starting')
                elif act==1 and self.sys_state == sys_globals.System_State.SYS_EXITING:
                    self.node_handler_entity.system_event_report(code='ESYS_IN_EXIT', desc=', system is exiting')
                elif act==1 and self.sys_state > 6:
                    self.node_handler_entity.system_event_report(code='ESYS_NOT_ALLOW_AUTOPILOT_FOR_REMOTE', desc=', system state have some fault')
                else:
                    pass

        elif reason == sys_globals.System_State.STATE_CHANGE_BY_REAL_VEHICLE_STATE: # vehicle state
            print('autopilot state change from {} to {}'.format(self.auto_polit_state, act))
            self.auto_polit_state = act
            if act == 0: 
                if self.show_mode_flag == True:
                    self.node_handler_entity.set_pilot_mode(1)
                    # Mark: if set_pilot_mode failed, there not change sys_globals.System_State !
                elif self.sys_state in (sys_globals.System_State.SYS_RUNNING, sys_globals.System_State.AUTO_PILOT_RUNNING):
                    self.set_sys_state_and_save(sys_globals.System_State.AUTO_PILOT_READY)
            else:
                if self.auto_polit_wait_thread and self.auto_polit_wait_thread.isAlive():
                    self.auto_polit_wait_thread.cancel()
                    self.set_sys_state_and_save(sys_globals.System_State.AUTO_PILOT_RUNNING)
                else:
                    print('polit mode change to 1 but no wait thread, unexpect!!')

        elif reason == sys_globals.System_State.STATE_CHANGE_BY_SYS_REBOOT_CMD:  # reboot
            self.set_sys_state_and_save(sys_globals.System_State.SYS_EXITING)

        else:   # sys event
            pass

    def wait_autopolit_succ(self):
        """
        #@name: 
        #@msg: timer callback,  AUTO_POLIT_START_WAIT_TIME has after, will call diagnose
        #@return {*}
        """
        
        if self.auto_polit_state != 1:
            print('start autopilot failed! while check state')
            # self.set_sys_state_and_save(sys_globals.System_State.SYS_EXITING)  # the state 
            self.node_handler_entity.system_event_report(code='ESYS_AUTOPILOT_FAILED', desc='')
            self.set_sys_state_and_save(sys_globals.System_State.AUTO_PILOT_READY)
            self.node_handler_entity.pub_system_diagnose_cmd()
            # TODO: do something make system ok ? or wait system reboot cmd?
        else:
            self.set_sys_state_and_save(sys_globals.System_State.AUTO_PILOT_RUNNING)
            print('The case should not ingress, there must have async error!')

    def system_off_process(self):
        print('start reboot system!!')
        self.system_reboot_flag = True
        ret = self.agent_handler_entity.send_cmd_to_agent(cmd='off')
        if ret is True:
            print('all agent stopping')
            # TODO: wait all agent stop complete
        else:
            print('Maybe send to some agent failed')

    def system_on_process(self):
        ret = self.agent_handler_entity.send_cmd_to_agent(cmd='on')
        if ret is True:
            print('all agent starting')
            # TODO: wait all agent start complete
        

    def handle_system_reboot(self):
        print('all agent will reboot!')
        self.change_sys_state(reason=3, act=0)
        t = threading.Thread(target=self.system_off_process, name='System reboot handle process')
        t.setDaemon(True)
        t.start()


    def init_master_node(self):
        """
        #@name: 
        #@msg: roscore is up, init system master node
        #@return {*}
        """

        if not self.node_spin_thread or not self.node_spin_thread.isAlive():
            print('roscore already working, Now init node!')
            try:
                rospy.init_node('system_master')  # this is not work, one python process can only run one node  
                self.node_handler_entity = Node_Handler()
                self.node_spin_thread = thread_with_trace(target=self.node_handler_entity.run, name='System Master spin thread')
                self.node_spin_thread.setDaemon(True)
                self.node_spin_thread.start()
                print('Thread create ok: ', self.node_spin_thread.getName())
            except Exception as e:
                print('init_master_node have some error happen: {}'.format(e))
    
    def stop_master_node(self):
        """
        #@name: 
        #@msg: roscore is down, stop all thread of system_master node
        #@return {*}
        """
        
        if self.node_spin_thread and self.node_spin_thread.isAlive():
            print('roscore is shutdown, the agent find and reported!')
            try:
                self.node_handler_entity.send_roscore_coredump_event()
                rospy.signal_shutdown('roscore is shutdown')
                time.sleep(0.5)
                self.node_spin_thread.kill() 
                self.node_spin_thread.join() 
                if not self.node_spin_thread.isAlive(): 
                    print('The thread of system_master node had killed')
                    # reboot self and wait agent connect
                    # os.kill(os.getgid(), 15)
                    os._exit(0)
            except Exception as e:
                print('stop_master_node have some error happen: {}'.format(e))

    def all_node_worked(self):
        ## check is get roscore starting msg
        self.init_master_node()
        if self.sys_state == sys_globals.System_State.SYS_STARTING:
            self.change_sys_state(reason=0, act=sys_globals.Agent_State.AGENT_NODES_WORKED)

    def all_node_stoped(self):
        if self.node_spin_thread and self.node_spin_thread.isAlive():
            ## not get roscore stopped msg
            print('allnode is shutdown, but master not stop!')
            self.stop_master_node()
        else:
            print('all rosnode stopped! here can start again')
            self.system_on_process()

    def handle_part_node_worked(self):
        """
        #@name: 
        #@msg:  handle part node worked, there need add some handle later
        #@return {*}
        """
        if self.sys_state > sys_globals.System_State.SYS_RUNNING:
            # add 20220526 ignore part node worked state after all node already worked
            # TODO add more handle
            return
        self.init_master_node()

    def run(self):
        self.agent_handler_entity.run()
        while True:
            try:
                self.agent_handler_entity.check_all_agent_timeout()
                if self.node_handler_entity and self.node_spin_thread.isAlive():
                    self.node_handler_entity.check_can_adapter_pub_msg()
                time.sleep(0.5)
            except Exception as e:
                print('System_Master.run have some error happen: {}'.format(e))
        

if __name__ == '__main__':
    print('\r\nsystem master start! version is {}'.format(sys_config.SYSTRM_MASTER_VERSION))
    sys_globals.g_system_master_entity = System_Master()
    sys_globals.g_system_master_entity.run()

