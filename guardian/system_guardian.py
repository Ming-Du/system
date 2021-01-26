#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import rosnode
import rosparam
import os
from threading import Thread
from std_msgs.msg import String
import json
import psutil
import collections
import sys
import simplejson
import logging
import re
import time
from subprocess import Popen,PIPE,STDOUT
logging.basicConfig()
class Process(Thread):
  config_file = ""
  NodeAlive = []
  NodeList=[]
  ParamName='/system/isReady'  #logDetail
  node_state_dict={}
  
  def __init__(self,filename):
    Thread.__init__(self)
    self.daemon = True
    self.config_file = filename
    self.register()
    self.start()
    
  def run(self):
    pub_node = rospy.Publisher('/system/nodes',String, queue_size=100)
    pub_cpu = rospy.Publisher('/system/cpu',String, queue_size=100)
    pub_mem = rospy.Publisher('/system/mem',String, queue_size=100)
    
    rate = rospy.Rate(1)
    while True:
      ps_num = 0
      self.node_state_dict = {}
      d = os.popen("rosnode list")
      node_li = d.read()
      self.NodeAlive = node_li.split("\n")
      print self.NodeAlive
      for node_name in self.NodeList:
        if node_name in self.NodeAlive:
            rospy.loginfo(node_name +" on") 
            self.node_state_dict[node_name] = "on" 
            ps_num +=1
        else:
            rospy.logerr(node_name + " is off, trying to restart...")
            self.node_state_dict[node_name] = "off"
            self.start_node(node_name)
      #node_list = [ node for node in rosnode.get_node_names() if node not in '/rosout' ]
      
      #for node_name in self.NodeList:
      #  pid = os.popen("ps -ef | grep __name:=" 
      #    + node_name 
      #    + " | grep -v 'grep' | awk '{print $2}'").read()
      #  
      if ps_num is len(self.NodeList):
        rospy.logwarn('system is ok')
        rosparam.set_param(self.ParamName, '1')
      else:
        rosparam.set_param(self.ParamName, '0')
      #print (self.node_state_dict)
      #nodestat
      nodemsg=json.dumps(self.node_state_dict)
      pub_node.publish(nodemsg)
      print nodemsg
      #cpustat
      cpu_dict=collections.OrderedDict()
      #cpu_dict={}
      cpunum = 0
      cpu_all = psutil.cpu_percent(0)
      cpu_dict["all"] = cpu_all
      cpu_per = psutil.cpu_percent(percpu=True)
      for i in cpu_per:
        cpunum=cpunum + 1
        cpuname = "cpu%s"%cpunum
        cpu_dict[cpuname] = i
      cpumsg = json.dumps(cpu_dict)
      pub_cpu.publish(cpumsg) 
      print(cpumsg)
      #memstat
      mem_info = psutil.virtual_memory()
      mem_dict = {}
      #print (type(mem_info.total))
      mem_dict["total_mem"] = "%dM"%(mem_info.total/(1024*1024))
      mem_dict["used_mem"] = "%dM"%(mem_info.used/(1024*1024))
      mem_dict["free"] = "%dM"%(mem_info.free/(1024*1024))
      mem_dict["percent_mem"] = "%s"%(mem_info.percent)

      memmsg = json.dumps(mem_dict)
      pub_mem.publish(memmsg)
      #print(dict)
      print(memmsg)
      print('---------')
      rate.sleep()
  
  def start_node(self, node):
    #if node is 'drivers_camera':
    pass
 
  def register(self):
    # drivers
    rospy.loginfo("configfile:%s"%self.config_file)
    with open(self.config_file,'r') as f:
        config = simplejson.load(f)
    guardian_nodes = config["guardian_nodes"]
    for i in guardian_nodes:
        self.NodeList.append(i)
    
    # telematics
    #self.NodeList.append('telematics');
    
    #self.NodeList.append('system_guardian')
    #rospy.Subscriber("/sensor/gnss/gps_fix")
    #if (status.status == 2) is fine

def topicFun(config_file,rostopic_file):
    topic_list=[]
    topic_send_list=[]
    rospy.loginfo("config_file:%s"%config_file)
    with open(config_file,'r') as f:
        config = simplejson.load(f)
    guardian_topics=config["guardian_topics"]
    for topic_g in guardian_topics:
        topic_list.append(topic_g) ######monitor topics
    topics_size = len(topic_list)
    pub_topics = rospy.Publisher('/system/rostopics',String, queue_size=100)
    while True:
        topic_str=""
        topic_monitor_list=[]
        count = 0
        p = Popen("rostopic list",shell=True,stdout=PIPE)
        topic_li = p.stdout.read()
        topicAlive = topic_li.split("\n")
        #print(topicAlive)
        for topic_g in topic_list:
            if topic_g in topicAlive:
                topic_str=topic_str +" " + topic_g  ######rostopic
                topic_monitor_list.append(topic_g)
        topics_size = len(topic_monitor_list)
        print("topics_size:%d"%topics_size)
        cmd = "python " + rostopic_file + " hz --window=50 " +  topic_str
        print(cmd)
        r = Popen(cmd, shell=True, stdout=PIPE,stderr=STDOUT)
        topic_dict = {}
        topic_dict_list = []
        for line in iter(r.stdout.readline, b''):
            line = line.strip('\n')
            line = line.strip()
            out_list=re.split(r'\s+',line)
            print("out_list[0]:%s"%out_list[0])
            if topics_size==1:
                if out_list[0]=="average":
                    topic_dict[topic_list[0]] = out_list[2]
                    topicsmsg = json.dumps(topic_dict)
                    print(topicsmsg)
                    pub_topics.publish(topicsmsg)
            if out_list[0]=="topic":
                for topic_g in topic_list:
                    if topic_g not in topic_dict_list:
                        topic_dict[topic_g]  = '0'
                topicsmsg = json.dumps(topic_dict)
                print(topicsmsg)
                pub_topics.publish(topicsmsg)
                count = 0
                topic_dict = {}
                topic_dict_list = []

            if 'WARING' in out_list:
                p.terminate()
                r.terminate()
                print(out_list)
                break
            if out_list[0] in topic_list:
                topic_dict[out_list[0]] = out_list[1]
                print(out_list[0]+":"+out_list[1])
                topic_dict_list.append(out_list[0])
            if out_list[0]=='no':
                print(out_list[0]+":"+out_list[0])
                topic_dict_list  = []
                for topic_g in topic_list:
                    if topic_g not in topic_dict_list:
                        topic_dict[topic_g]  = '0'
                topicsmsg = json.dumps(topic_dict)
                print(topicsmsg)
                pub_topics.publish(topicsmsg)
                count = 0
                topic_dict = {}
                topic_dict_list = []

def main():
    if len(sys.argv) < 3:
        rospy.logerr("please use:system_guardian.py configfilename, rostopicfilename")
        exit(-1)
    rospy.init_node('system_guardian')
    config_file = sys.argv[1].strip()
    rostopic_file = sys.argv[2].strip()
    pth_topic = Thread(target=topicFun,args=(config_file,rostopic_file))
    print("pth:config_file:%s"%config_file) 
    print("pth:rostopic_file:%s"%rostopic_file)
    pth_topic.setDaemon(True)
    pth_topic.start()

    p = Process(config_file)
    rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print "user ctrl-c to exit"
        exit(0)
