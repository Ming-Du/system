#!/usr/bin/env python
import os
import sys
import traceback
import json
from math import modf
import time

class MOGO_MSG(object):
    def __init__(self,ID=__file__,logdir='/home/mogo/data/log'):
        self.ID = ID
        self.config_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'mogo_report_msg.json')
        if logdir == '/home/mogo/data/log':
            self.logdir = os.path.join(logdir, 'msg_log')
        else:
            self.logdir = os.path.join(logdir, '../msg_log')
        self.logfile = os.path.join(self.logdir,'roslaunch_report.json')
        self.json_config_str = {}
        self.state = False
        self.strerror = ''

    def init(self):
        try:
            with open(self.config_file,"r") as f:
                self.json_config_str = json.loads(f.read())
        except IOError as e:
            self.strerror = e.strerror
            traceback.print_exc()
            self.state = False
            return False
        try:
            if not os.path.exists(self.logdir):
                os.makedirs(self.logdir)
        except OSError as e:
            self.strerror = e.strerror
            traceback.print_exc()
            self.state = False
            return False
        self.state = True
        return True
    
    def mogo_write(self, no, msg):
        if not self.state:
            sys.stderr.write('write mogo message to file error:%s'%self.strerror)
            return
        msg_obj = self.json_config_str.get(no)
        if msg_obj is None:
            msg_obj = {}
        (ns,s) = modf(time.time())
        timestamp = {"sec":int(s),"nsec":int(ns * 1e9)}
        msg_obj["timestamp"] = timestamp
        msg_obj["src"] = self.ID
        msg_obj["msg"] = msg.replace('\n','')
        os.popen('echo "%s">>%s'%(json.dumps(msg_obj).replace(r'"',r'\"'),self.logfile))