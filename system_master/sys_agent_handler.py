#!/usr/bin/python
# -*- coding:utf-8 -*-

'''
Author: your name
Date: 2022-04-27 18:11:56
LastEditTime: 2022-05-18 12:55:16
LastEditors: liyuelei liyuelei@zhidaoauto.com
Description: the file handel the msg form agent
FilePath: /catkin_ws/src/system/system_master/sys_agent_handler.py
'''

import sys
import time
import Queue
import threading
import sys_globals, sys_config
from sys_globals import g_all_agent_list, g_master_httpd_port, Agent_State, SysCmd_to_Agent
from sys_common import ssh_command

import SimpleHTTPServer
import SocketServer


class Resquest(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        # test: curl -d "action=2,time=sec.usec" 192.168.13.131:8080

        #获取post提交的数据
        datas = self.rfile.read(int(self.headers['content-length']))    #固定格式，获取表单提交的数据
        #print('get datas:', datas.split(','))
        req_d = datas.split(',')
        rsp_d = 'no action keywords, req is {}\n'.format(datas)
        if len(req_d) == 2 and 'action' in req_d[0] and 'time' in req_d[1]:
            if self.client_address[0] not in g_all_agent_list:
                print('First time receive agent {}'.format(self.client_address[0]))
                g_all_agent_list[self.client_address[0]] = dict()
            act = int(req_d[0].split('=')[1])
            cur_t = float(req_d[1].split('=')[1])
            if act in Agent_State.State_Desc:
                g_all_agent_list[self.client_address[0]]['last_access_time'] = time.time()
                g_all_agent_list[self.client_address[0]]['agent_time'] = cur_t
                if g_all_agent_list[self.client_address[0]].get('current_state', -1) != act:
                    print('The agent {} state changed from {} to {}'.format(
                        self.client_address[0], g_all_agent_list[self.client_address[0]].get('current_state', -1), act))
                    g_all_agent_list[self.client_address[0]]['current_state'] = act
                    sys_globals.g_system_master_entity.agent_handler_entity.agent_msg_queue.put(act)
                    # sys_globals.g_system_master_entity.agent_handler_entity.handle_agent_action(act)
                rsp_d = 'reveice success!\n'
            else:
                rsp_d = 'the action unexpect!\n'
        self.send_response(200)
        #self.send_header("Content-type","text/html")    #设置post时服务器的响应头
        #self.send_header("test","This is post!")
        self.end_headers()
    
        self.wfile.write(rsp_d.encode())
        #print(g_all_agent_list)

class My_Httpd(SocketServer.TCPServer):
    allow_reuse_address = True

class Agent_Handler(object):
    def __init__(self):
        self.all_agent_start_flag = False
        self.agent_info_list = g_all_agent_list
        self.host = ("", g_master_httpd_port)
        self.agent_num = self.get_agent_info()
        self.agent_msg_queue = Queue.Queue(128)
        self.httpd = My_Httpd(self.host, Resquest)
    
    @staticmethod
    def get_agent_info():
        """
        need get agent info for /etc/host
        """
        with open('/etc/hosts', 'r') as fd:
            context = fd.read()
        
        agent_num = 0
        for line in context.split('\n'):
            if 'ros' in line:
                agent_num += 1

        return agent_num


    def handle_agent_action(self, action):
        """
        #@name: 
        #@msg: handle agent msg when action code changed
        #@return { None }
        """
        print('Have agent report action {}'.format(Agent_State.State_Desc[action]))
        if not self.all_agent_start_flag and self.agent_num == len(self.agent_info_list):
            self.all_agent_start_flag = True

        if action == Agent_State.AGENT_ROSCORE_RUN:
            sys_globals.g_system_master_entity.init_master_node()
        elif action == Agent_State.AGENT_ROSCORE_DOWN:
            sys_globals.g_system_master_entity.stop_master_node()
        elif action == Agent_State.AGENT_NODES_WORKED:
            if self.check_all_agent_work():
                sys_globals.g_system_master_entity.all_node_worked()
                # sys_globals.g_system_master_entity.change_sys_state(reason=0, act=Agent_State.AGENT_NODES_WORKED)
        elif action == Agent_State.AGENT_NODES_STOPPED:
            if self.check_all_agent_stop():
                sys_globals.g_system_master_entity.all_node_stoped()
                # sys_globals.g_system_master_entity.change_sys_state(reason=0, act=Agent_State.AGENT_NODES_STOPPED)
        elif action == Agent_State.AGENT_NODE_PART_WORKED:
            if sys_config.g_local_test_flag:
                if self.test_all_agent_work():
                    sys_globals.g_system_master_entity.all_node_worked()
            else:
                #TODO: this case may make system fault
                sys_globals.g_system_master_entity.handle_part_node_worked()

    def test_all_agent_work(self):
        """
        #@name: check agent work status
        #@msg: In local testing the node_port_worked state which we think is running normally maybe need modify later
        #@return { True if all agent worked else False}
        """
        
        if not self.all_agent_start_flag:
            return False
        ret = True
        for agent in self.agent_info_list.values():
            if agent['current_state'] not in (Agent_State.AGENT_NODES_WORKED, Agent_State.AGENT_NODE_PART_WORKED):   
                ret = False
                break
        return ret

    def check_all_agent_work(self):
        """
        #@name: check agent work status
        #@msg:  mod 20220526 fix AGENT_NODE_PART_WORKED state error handle
        #@return { True if all agent worked else False}
        """
        
        if not self.all_agent_start_flag:
            return False
        ret = True
        for agent in self.agent_info_list.values():
            if agent['current_state'] != Agent_State.AGENT_NODES_WORKED:   
                ret = False
                break
        return ret

    def check_all_agent_stop(self):
        if not self.all_agent_start_flag:
            return False
        ret = True
        for agent in self.agent_info_list.values():
            if agent['current_state'] != Agent_State.AGENT_NODES_STOPPED:   
                ret = False
                break
        return ret  


    def check_all_agent_timeout(self):
        """
        #@name: 
        #@msg: handle agent msg form queue, and check agent_info_list time state
        #@return {*}
        """

        while not self.agent_msg_queue.empty():
            act = self.agent_msg_queue.get()
            self.handle_agent_action(act)
            
        if not self.all_agent_start_flag:
            return

        cur_time = time.time()
        all_agent_start_flag = True
        for ip, agent in self.agent_info_list.items():
            if agent['current_state'] is Agent_State.AGENT_NODES_STOPPED:
                all_agent_start_flag = False
                break
            if agent['last_access_time'] + sys_config.HEARTBEAT_TIMEOUT_OF_AGENT < cur_time:
                err_msg = 'Agent[{}] timeout !!'.format(ip)
                print('{},{},{}'.format(err_msg, agent['last_access_time'], cur_time))
                # TODO: timeout handle
                # all_agent_start_flag = False

        self.all_agent_start_flag = all_agent_start_flag

    def parse_mian_pid_of_agent(self, results):
        """
        #@name: 
        #@msg:  get agent pid for fix bug adsa-161
        #@return {pid of 0}
        """
        ppid = -1
        for line in results.split('\n'):
            ret = line.split()
            if len(ret) > 7:
                try:
                    ppid_tmp, pid_tmp = int(ret[1]), int(ret[2])
                except:
                    print("ret[{}] not have pid".format(ret))
                    continue

                if ppid == -1 and pid_tmp in (0,1):
                    ppid = ppid_tmp
                elif ppid == pid_tmp:
                    print("find ppid success! ppid={}".format(ppid))
                    break

        return ppid
    
    def send_cmd_to_agent(self, cmd):
        """
        #@name: 
        #@msg: when systemcmd is reboot, the ssh cmd will sendto all agent
        #@return {*}
        """
        
        ret = True
        for ip, agent in self.agent_info_list.items(): 
            get_pid_cmd = SysCmd_to_Agent.Get_Agent_Pid.format(ip)
            status, results = ssh_command(SysCmd_to_Agent.g_agent_mogo_pwd, get_pid_cmd)
            
            if status or not results:
                print('Exec get_pid_cmd error! agent_ip={}'.format(ip))
                print('cmd result:', status, results)
                ret = False
                break
            
            pid_str = self.parse_mian_pid_of_agent(results)
            if pid_str > 0:
                print('get agent {} pid is {}'.format(ip, pid_str))
                if cmd == 'off':
                    kill_cmd = SysCmd_to_Agent.Xavier_Off.format(ip, pid_str)
                else:
                    kill_cmd = SysCmd_to_Agent.Xavier_On.format(ip, pid_str)
                status, result = ssh_command(SysCmd_to_Agent.g_agent_mogo_pwd, kill_cmd)
                if status:  # cmd failed!
                    ret = False
                else:
                    print('cmd exec success! [{}], ret=[{}]'.format(kill_cmd, result))
            else:
                print('Not find agent pid, cmd send failed!!')
                ret = False
                break
        
        return ret  

    def run(self):
        t = threading.Thread(target=self.httpd.serve_forever, name='Http server for Agent connect')
        t.setDaemon(True)
        t.start()
        print('Thread create ok:', t.getName())


if __name__ == '__main__':
    a = Agent_Handler()
    a.run()
    while True:
        print('get agent:', a.agent_info_list)
        time.sleep(5)
        for x in a.agent_info_list.values():
            if x.get('current_state', 1) == 2:
                sys.exit()
