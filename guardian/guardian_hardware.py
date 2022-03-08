#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import sys
import time
import datetime
import rospy
import rosnode
import rosparam
from std_msgs.msg import String, UInt8, Int32
from rospy import init_node, Subscriber, Publisher
from threading import Thread

class Tail(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        
        nowtime = time.strftime('%Y%m%d',time.localtime(time.time()))
        yeartime = time.strftime('%Y',time.localtime(time.time()))
        week=datetime.datetime.strptime(nowtime,'%Y%m%d').strftime('%W')
        self.file_name = "/home/mogo/data/vehicle_monitor/data/" + "mtop-"+yeartime+week+"-week.json"
        self.hardware_pub = rospy.Publisher('/system/hardware',String, queue_size=100)
        rospy.loginfo ("dockeragent:" + self.file_name)
        self.start()
    def run(self):
        self.follow()
    def initAgentline(self):
        self.sysAgentline = ""

    def follow(self):
        try:
            self.initAgentline();
            with open(self.file_name) as f:
                f.seek(0,2)
                while True:
                    linetmp = f.readline()
                    self.sysAgentline = self.sysAgentline + linetmp
                    if self.sysAgentline and self.sysAgentline[-1] == '\n':
                        #self.callback(self.sysagentline)
                        self.getCan()
                        self.initAgentline()
                        
                    time.sleep(0.01)
        
        except Exception,e:
            rospy.logerr("error:")
            rospy.logerr(e)

    def getCan(self):
        self.agent_dict = json.loads(self.sysAgentline)
        self.modules = self.agent_dict["modules"]
        self.hardpub()
        """
        for module in self.modules:
            if module["name"] == "IPC":
                for  submodule in module["subModules"]:
                    if submodule["name"] == "can0":
                        #print("sub:") 
                        #print(submodule)   
                        self.can0Stat_dict = submodule
                    if submodule["name"] == "can1":
                        self.can1Stat_dict = submodule 
                
    
        print("can0:" + json.dumps(self.can0Stat_dict))                     
        print("can1:" + json.dumps(self.can1Stat_dict))         
        print("agent:" + json.dumps(self.agent_dict))            
        """
    def hardpub(self):
        self.hardware_pub.publish(json.dumps(self.agent_dict))
