#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import rosnode
import rosparam
import os
from threading import Thread
import threading
from std_msgs.msg import String
import json
import psutil
import collections
import sys
import simplejson
import logging
import re
import time
import datetime
from subprocess import Popen,PIPE,STDOUT
from multiprocessing import Process, Manager
import multiprocessing
from std_msgs.msg import String, UInt8, Int32
from rospy import init_node, Subscriber, Publisher
import guardian_hardware
import gethosttopic
import proto.log_reslove_pb2 as common_log_reslove_pb2
from autopilot_msgs.msg import BinaryData
logging.basicConfig()

flow_dict = {}
class Process(Thread):
  config_file = ""
  NodeAlive = []
  NodeList=[]
  ParamName='/system/isReady'  #logDetail
  node_state_dict={}
  
  def __init__(self, vehiclefile):
    Thread.__init__(self)
    self.daemon = True
    #self.config_file = filename
    self.vehiclefile = vehiclefile
    self.register()
    self.start()
    
  def run(self):
    print "entet run =========="
    pub_node = rospy.Publisher('/system/nodes',String, queue_size=100)
    pub_cpu = rospy.Publisher('/system/cpu',String, queue_size=100)
    pub_mem = rospy.Publisher('/system/mem',String, queue_size=100)
    pub_disk = rospy.Publisher('/system/disk',String, queue_size=100)
    pub_progcpu = rospy.Publisher('/system/program/cpu',String, queue_size=100)
    pub_progmem = rospy.Publisher('/system/program/mem',String, queue_size=100)
    pub_netflow = rospy.Publisher('/system/netflow',String, queue_size=100)
    print "before rospy.Rate===="
    rate = rospy.Rate(1)
    while True:
      print "enter run_while===="
      ps_num = 0
      self.node_state_dict = {}
      #d = os.popen("rosnode list")
      #node_li = d.read()
      #self.NodeAlive = node_li.split("\n")
      self.NodeAlive = self.node_ping_alive()
      print self.NodeAlive
      print "self.NodeList==="
      print self.NodeList
      for node_name in self.NodeList:
        if node_name in self.NodeAlive:
            rospy.loginfo(node_name +" on") 
            self.node_state_dict[node_name] = "on" 
            ps_num +=1
        else:
            #rospy.logerr(node_name + " is off, trying to restart...")
            rospy.logerr(node_name + " is off")
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
      '''
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
      #diskstat
      disk_dict = {}
      #cmd="df -h |grep -w -E '/|/data' |awk -F' ' '{print $1 \" \" $2 \" \" $3 \" \" $4 \" \" $5 \" \" $6}'"
      cmd="df -h |grep '/' |awk -F' ' '{print $1 \" \" $2 \" \" $3 \" \" $4 \" \" $5 \" \" $6}'"
      rdisk = Popen(cmd, shell=True, stdout=PIPE,stderr=STDOUT)
      for line in iter(rdisk.stdout.readline, b''):
          line = line.strip('\n')
          #print(line)
          out_list=re.split(r' ',line)
          dict_tmp = {}
          dict_tmp["diskname"]=out_list[0]
          dict_tmp["diskall"]=out_list[1]
          dict_tmp["diskuse"]=out_list[2]
          dict_tmp["diskfree"]=out_list[3]
          dict_tmp["diskpercent"]=out_list[4]
          dict_tmp["diskmount"]=out_list[5]
          disk_dict[out_list[0]] = dict_tmp;
          #print(out_list)
      rdisk.terminate()
      diskmsg = json.dumps(disk_dict)
      pub_disk.publish(diskmsg)
      print(diskmsg)
      print('---------')
      #top ten %cpu program
      #top_cmd = "ps aux|head -1|awk -F' ' '{print$3,$4,$11}';ps aux|grep -v PID|sort -rn -k +3|head|awk -F' ' '{print$3,$4,$11,$12}'" 
      #top_cmd = "ps aux|grep -v PID|sort -rn -k +3|head|awk -F' ' '{print$3,$4,$11,$12}'" 
      top_cmd = "ps aux|grep -v PID|sort -rn -k +3" 
      top_cmd1 = "head|awk -F' ' '{print$3,$4,$11,$12}'" 
      prog1 = Popen(top_cmd, shell=True, stdout=PIPE)
      prog = Popen(top_cmd1, shell=True, stdin=prog1.stdout, stdout=PIPE)
      prog_dict = {}
      for line in iter(prog.stdout.readline, b''):
          #print(line)
          out_list = re.split(r' ', line)
          dict_tmp = {}
          if len(out_list)==3:
            tmp = out_list[2]
          elif len(out_list) > 3:
            if "python" in out_list[2]:
                tmp = out_list[3]
            else:
                tmp = out_list[2]
          #print(tmp)
          dict_tmp["prog_name"] = tmp
          dict_tmp["cpu_percent"] = out_list[0]
          dict_tmp["mem_percent"] = out_list[1]
          prog_dict[tmp] = dict_tmp
      prog1.terminate()
      prog.terminate()
      progmsg = json.dumps(prog_dict)
      pub_progcpu.publish(progmsg)
      print(progmsg)
      #top ten %mem  program
      top_cmd = "ps aux|grep -v PID|sort -rn -k +4" 
      top_cmd1 = "head|awk -F' ' '{print$3,$4,$11,$12}'" 
      prog_mem1 = Popen(top_cmd, shell=True, stdout=PIPE)
      prog_mem = Popen(top_cmd1, shell=True, stdin=prog_mem1.stdout, stdout=PIPE)
      progmem_dict = {}
      for line in iter(prog_mem.stdout.readline, b''):
      #print(line)
          out_list = re.split(r' ', line)
          dict_tmp = {}
          if len(out_list)==3:
            tmp = out_list[2]
          elif len(out_list) > 3:
            if "python" in out_list[2]:
                tmp = out_list[3]
            else:
                tmp = out_list[2]
          #print(tmp)
          dict_tmp["prog_name"] = tmp
          dict_tmp["cpu_percent"] = out_list[0]
          dict_tmp["mem_percent"] = out_list[1]
          progmem_dict[tmp] = dict_tmp
      prog_mem1.terminate()
      prog_mem.terminate()
      progmemmsg = json.dumps(progmem_dict)
      pub_progmem.publish(progmemmsg)
      print(progmemmsg)
      #net-flow
      self.flow_dict = {}
      net_list = []
      for Net_card in self.get_netcard():
          #netp = multiprocessing.Process(target=self.Net_card_flow, args=(Net_card,))
          self.Net_card_flow(Net_card)
          break
          #netp.daemon=True
          #net_list.append(netp)
      #for p in net_list:
          #p.start()
      #for p in net_list:
          #p.join()
      netmsg = json.dumps(self.flow_dict)
      pub_netflow.publish(netmsg)
      '''

      rate.sleep()
  
  def start_node(self, node):
    #if node is 'drivers_camera':
    pass
 
  def register(self):
    # drivers
    rospy.loginfo("configfile:%s"%self.vehiclefile)
    guardian_nodes = nodeconfig(self.vehiclefile)
      

    for i in guardian_nodes:
        self.NodeList.append(i)
    
    # telematics
    #self.NodeList.append('telematics');
    
    #self.NodeList.append('system_guardian')
    #rospy.Subscriber("/sensor/gnss/gps_fix")
    #if (status.status == 2) is fine
  def get_netcard(self):
        netcard_info = []
        info = psutil.net_if_addrs()
        for k,v in info.items():
            for item in v:
                if item[0] == 2 and not item[1]=='127.0.0.1':
                    netcard_info.append((k))
        return netcard_info

  def Net_card_flow(self, get_net):
        Sent_flow_1 = (psutil.net_io_counters(pernic=True)[get_net]).bytes_sent
        Recv_flow_1 = (psutil.net_io_counters(pernic=True)[get_net]).bytes_recv
        time.sleep(0.5)
        Sent_flow_2 = (psutil.net_io_counters(pernic=True)[get_net]).bytes_sent
        Recv_flow_2 = (psutil.net_io_counters(pernic=True)[get_net]).bytes_recv

        #计算当前流量的字节数
        Sent_flow = (Sent_flow_2-Sent_flow_1)*2.0
        Recv_flow = (Recv_flow_2-Recv_flow_1)*2.0
        #计算发送流量
        if Sent_flow < 1024:
            Sent_flow_format = str(Sent_flow )+"B/s"
        elif 1024 <= Sent_flow < 1048576:
            Sent_flow_format = str(Sent_flow/1024)+"K/s"
        elif 1048576 <= Sent_flow < 1073741824:
            Sent_flow_format = str(Sent_flow/1024/1024 )+"M/s"
        else:
            Sent_flow_format = str(Sent_flow/1024/1024/10240)+"G/s"

        #计算接受流量
        if Recv_flow  < 1024:
            Recv_flow_format = str(Recv_flow)+"B/s"
        elif 1024 <= Recv_flow < 1048576:
            Recv_flow_format = str(Recv_flow/1024)+"K/s"
        elif 1048576 <= Recv_flow < 1073741824:
            Recv_flow_format = str(Recv_flow/1024/1024)+"M/s"
        else:
            Recv_flow_format = str(Recv_flow/1024/1024/1024)+"G/s"

        #print "网卡:",get_net," \t发送流量:",Sent_flow_format,"接受流量:",Recv_flow_format
        net_dict = {}
        self.flow_dict = {}
        net_dict["netname"] = get_net
        net_dict["send_flow"] = Sent_flow_format
        net_dict["recv_flow"] = Recv_flow_format
        self.flow_dict[get_net] = net_dict
        #print(self.flow_dict)
        #print(netmsg)
        #print(flow_dict)

  def node_ping_alive(self):
      ping_flag = False
      node_alive_li = []
      prog = Popen("rosnode ping -a", shell=True, stdout=PIPE)
      node_li = prog.stdout.read()
      #output = prog.communicate()
      #output_li = list(output)
      node_li = node_li.split("\n")
      for ping_line in node_li:
          ping_li = ping_line.split(" ")
          if ping_li[0] == "pinging":
             if ping_flag and len(node_alive_li) > 0:
                node_alive_li.pop()
             ping_flag = True
             node_alive_li.append(ping_li[1])
          else:
             ping_flag = False
      print(node_alive_li)
      return node_alive_li        
      
    
def topicFun(rostopic_file, brandtopicfile):
    global rosmachetype
    topic_orig_dict = {}
    topic_orig_list = []
    topic_list=[]
    topic_send_list=[]
    guardian_topics = topicconfig(brandtopicfile)
    print("guardian_topics") 
    print(guardian_topics) 
    for topic_g in guardian_topics:
        topic_g_list = []
        topic_g_list = topic_g.split(':')
        topic_list.append(topic_g_list[0]) ######monitor topics
        if( len(topic_g_list) >= 2 ):
            topic_orig_dict[topic_g_list[0]] = topic_g_list[1];
        else:
            topic_orig_dict[topic_g_list[0]] = "";
        
    topics_size = len(topic_list)
    pub_topics = rospy.Publisher('/system/rostopics_hz',String, queue_size=100)
    topic_string  = '/system/rostopics_hz_' + rosmachetype
    pub_topics_slave = rospy.Publisher(topic_string,String, queue_size=100)
    def pubtopic_mache(msg):
        global rosmachetype;
        if rosmachetype != "master":
            pub_topics_slave.publish(msg)
        else:
            '''
            Guardian_sub.slave_mutex.acquire() 
            slavemsg = Guardian_sub.topicslavemsg 
            Guardian_sub.slave_mutex.release() 
            '''
            slavemsg1 = getslavemsg(Guardian_sub.slave_mutex1, Guardian_sub.topicslavemsg1)
            slavemsg2 = getslavemsg(Guardian_sub.slave_mutex2, Guardian_sub.topicslavemsg2)
            slavemsg3 = getslavemsg(Guardian_sub.slave_mutex3, Guardian_sub.topicslavemsg3)
            slavemsg4 = getslavemsg(Guardian_sub.slave_mutex4, Guardian_sub.topicslavemsg4)
            slavemsg5 = getslavemsg(Guardian_sub.slave_mutex5, Guardian_sub.topicslavemsg5)
            slavemsg6 = getslavemsg(Guardian_sub.slave_mutex6, Guardian_sub.topicslavemsg6)
            #rospy.loginfo("slavemsg:" + slavemsg)
            tmpmaster = json.loads(msg)
            tmpmaster = fusiontopic(slavemsg1, tmpmaster)
            tmpmaster = fusiontopic(slavemsg2, tmpmaster)
            tmpmaster = fusiontopic(slavemsg3, tmpmaster)
            tmpmaster = fusiontopic(slavemsg4, tmpmaster)
            tmpmaster = fusiontopic(slavemsg5, tmpmaster)
            tmpmaster = fusiontopic(slavemsg6, tmpmaster)
            msg  = json.dumps(tmpmaster)
            rospy.loginfo("fusionmsg:" + msg)
            pub_topics.publish(msg)
'''
    while True:
        topic_first = True;
        pub_first = True;
        topic_str=""
        topic_monitor_list=[]
        count = 0
        
        p = Popen("rostopic list -p",shell=True,stdout=PIPE)
        topic_li = p.stdout.read()
        topicAlive = topic_li.split("\n")
        #print(topicAlive)
        #print("topicalive:")
        #print(topicAlive)
        #print("topic_list_after:")
        #print(topic_list)
        
        topicAlive = gethosttopic.gethosttopics(); 
        for topic_g in topic_list:
            if topic_g in topicAlive:
                #print("yes:" + topic_g)
                topic_str=topic_str +" " + topic_g  ######rostopic
                topic_monitor_list.append(topic_g)
            else:
                pass
                #print("no:" + topic_g )

        topics_size = len(topic_monitor_list)
        #print("topics_size:%d"%topics_size)
        cmd = "python " + rostopic_file + " hz --window=50 " +  topic_str
        print(cmd)
        r = Popen(cmd, shell=True, stdout=PIPE,stderr=STDOUT)
        topic_dict = {}
        topic_dict_list = []
        tbegin = time.time()
        for line in iter(r.stdout.readline, b''):
            line = line.strip('\n')
            line = line.strip()
            out_list=re.split(r'\s+',line)
            #print(line)
            #print("out_list[0]:%s"%out_list[0])
            topic_msg_dict = {}
            if topics_size==1:
                print("topics_size=1")
                if out_list[0]=="average":
                    for topic_g in topic_list:
                        if topic_g not in topic_monitor_list:
                            topic_msg_dict["topic_name"] = topic_g
                            topic_msg_dict["run_hz"] = "0"
                            topic_msg_dict["set_hz"] = topic_orig_dict[topic_g]
                            topic_dict[topic_g]  = topic_msg_dict
                            topic_msg_dict = {}
                    topic_msg_dict["topic_name"] = topic_monitor_list[0]
                    topic_msg_dict["run_hz"] = str(out_list[2])
                    topic_msg_dict["set_hz"] = topic_orig_dict[topic_monitor_list[0]]
                    #topic_dict[topic_list[0]] = out_list[2]
                    topic_dict[topic_monitor_list[0]] = topic_msg_dict
                    topicsmsg = json.dumps(topic_dict)
                    print(topicsmsg)
                    #pub_topics.publish(topicsmsg)
                    pubtopic_mache(topicsmsg)
                    topic_first = False
            if out_list[0]=="topic":
                for topic_g in topic_list:
                    if topic_g not in topic_dict_list:
                        topic_msg_dict["topic_name"] = topic_g
                        topic_msg_dict["run_hz"] = "0"
                        topic_msg_dict["set_hz"] = topic_orig_dict[topic_g]
                        topic_dict[topic_g]  = topic_msg_dict
                        topic_msg_dict = {}
                if pub_first == False:
                    topicsmsg = json.dumps(topic_dict)
                    print(topicsmsg)
                    #pub_topics.publish(topicsmsg)
                    pubtopic_mache(topicsmsg)
                    topic_first = False
                else:
                    print("first pub")
                    pub_first = False

                count = 0
                topic_dict = {}
                topic_dict_list = []

            if 'WARING' in out_list:
                #p.terminate()
                r.terminate()
                print(out_list)
                break
            if out_list[0] in topic_list:
                topic_msg_dict["topic_name"] =out_list[0] 
                topic_msg_dict["run_hz"] = str(out_list[1])
                topic_msg_dict["set_hz"] = topic_orig_dict[out_list[0]]
                #topic_dict[out_list[0]] = out_list[1]
                topic_dict[out_list[0]] = topic_msg_dict;
                #print(out_list[0]+":"+out_list[1])
                topic_dict_list.append(out_list[0])
            if (out_list[0]=='no' or out_list[0] == 'Usage:') :
                print(out_list[0]+":"+out_list[0])
                topic_dict_list  = []
                for topic_g in topic_list:
                    if topic_g not in topic_dict_list:
                        topic_msg_dict["topic_name"] = topic_g
                        topic_msg_dict["run_hz"] = "0"
                        topic_msg_dict["set_hz"] = topic_orig_dict[topic_g]
                        #topic_dict[topic_g]  = '0'
                        topic_dict[topic_g]  = topic_msg_dict
                        topic_msg_dict = {}
                topicsmsg = json.dumps(topic_dict)
                    
                print("topicsmsg")
                if topic_first == False or out_list[0] == 'Usage:':
                    print(topicsmsg)
                    #pub_topics.publish(topicsmsg)
                    pubtopic_mache(topicsmsg)
                else:
                    print("topic_first")
                    topic_first = False
                count = 0
                topic_dict = {}
                topic_dict_list = []
            tend = time.time()
            if(tend - tbegin > 20.0):
                tbegin = time.time()
                #p.terminate()
                r.terminate()
                break;


        print("end for")
    print("end while") 
'''

def topicconfig(configfile):
    global brand
    global rosmachetype;
    topic_list = []
    node_list = []
    with open(configfile, 'r') as f:
        config = simplejson.load(f)
    for model in config:
        for node in  model["value"]:
            brand_list = node["brand"].split(":")
            machetype_config = node["rosmachetype"]
            for brand_tmp in brand_list:
                if brand_tmp.strip() == brand.strip():
                    #if  machetype_config.strip() == rosmachetype.strip() or rosmachetype.strip() == "single":
                    node_list.append(node["node_name"].strip())
                    for topic in node["value"]:
                        if brand.strip() in topic["brand"].split(":") and topic["guardian"] == "y":
                            if topic["topic_name"].strip() != '':
                                str_tmp = topic["topic_name"] + ":" + topic["set_hz"]
                                topic_list.append(str_tmp.strip())
    print("topic_list:")
    print(topic_list) 
    return topic_list              

def nodeconfig(configfile):
    global brand
    node_list = []
    with open(configfile, 'r') as f:
        config = simplejson.load(f)
    for model in config:
        for node in  model["value"]:
            brand_list = node["brand"].split(":")
            for brand_tmp in brand_list:
               if brand_tmp.strip() == brand.strip():
                    node_list.append(node["node_name"].strip())
    print("node_list:")
    print(node_list) 

    return node_list

def get_brand(vehicle_config):
    global brand
    f = open(vehicle_config);
    line = f.readline()
    while line:
        if(line.isspace()):
            line = f.readline()
        line = line.replace(" ", "")
        tmp = line.split(":")
        if(tmp[0] == "brand"):
            brand = tmp[1].replace("\"","")
            #brand = tmp[1]
            print("brand:" + brand)
            break;
        line  = f.readline()
    return brand
class Guardian_sub:
    topicslavemsg1 = ""
    topicslavemsg2 = ""
    topicslavemsg3 = ""
    topicslavemsg4 = ""
    topicslavemsg5 = ""
    topicslavemsg6 = ""
    slave_mutex1 = threading.Lock()
    slave_mutex2 = threading.Lock()
    slave_mutex3 = threading.Lock()
    slave_mutex4 = threading.Lock()
    slave_mutex5 = threading.Lock()
    slave_mutex6 = threading.Lock()
    def __init__(self):
        #rospy.Subscriber("/system/rostopics_hz_slave", String, self.topicslave_callback)
        pass
    def topicslave_callback1(self,msg):
        Guardian_sub.slave_mutex1.acquire()
        Guardian_sub.topicslavemsg1 = msg.data
        Guardian_sub.slave_mutex1.release()
    def topicslave_callback2(self,msg):
        Guardian_sub.slave_mutex2.acquire()
        Guardian_sub.topicslavemsg2 = msg.data
        Guardian_sub.slave_mutex2.release()
    def topicslave_callback3(self,msg):
        Guardian_sub.slave_mutex3.acquire()
        Guardian_sub.topicslavemsg3 = msg.data
        Guardian_sub.slave_mutex3.release()
    def topicslave_callback4(self,msg):
        Guardian_sub.slave_mutex4.acquire()
        Guardian_sub.topicslavemsg4 = msg.data
        Guardian_sub.slave_mutex4.release()
    def topicslave_callback5(self,msg):
        Guardian_sub.slave_mutex5.acquire()
        Guardian_sub.topicslavemsg5 = msg.data
        Guardian_sub.slave_mutex5.release()
    def topicslave_callback6(self,msg):
        Guardian_sub.slave_mutex6.acquire()
        Guardian_sub.topicslavemsg6 = msg.data
        Guardian_sub.slave_mutex6.release()
    def rosslavesub(self):
        self.slavesub1 = rospy.Subscriber("/system/rostopics_hz_slave1", String, self.topicslave_callback1)
        self.slavesub2 = rospy.Subscriber("/system/rostopics_hz_slave2", String, self.topicslave_callback2)
        self.slavesub3 = rospy.Subscriber("/system/rostopics_hz_slave3", String, self.topicslave_callback3)
        self.slavesub4 = rospy.Subscriber("/system/rostopics_hz_slave4", String, self.topicslave_callback4)
        self.slavesub5 = rospy.Subscriber("/system/rostopics_hz_slave5", String, self.topicslave_callback5)
        self.slavesub6 = rospy.Subscriber("/system/rostopics_hz_slave6", String, self.topicslave_callback6)
def getslavemsg(mu_mutex, topicslavemsg):
     mu_mutex.acquire()
     msg = topicslavemsg
     mu_mutex.release()
     return msg

def fusiontopic(slavemsg, tmpmaster):
    if slavemsg != "":
        tmpslave = json.loads(slavemsg)
        #for key in tmpslave.keys():
        #    run_hz = tmpslave[key]["run_hz"]
        #    if run_hz != "0" and run_hz != "":
        #        if tmpmaster.has_key(key):
         #           tmpmaster[key]["run_hz"] = run_hz  
        #tmpfusion = dict(tmpmaster.items() + tmpslave.items())
        #msg  = json.dumps(tmpfusion)
        for key in topicInfo.keys():
            run_hz = topicInfo[key]
            if tmpmaster.has_key(key):
                tmpmaster[key]["run_hz"] = str(run_hz)
    return tmpmaster
        
          
topicInfo = {}       
    
def topics_callback(msg):
    print "start recv topic hz ..."
    global topicsmsg
    global topicInfo
    topicsmsg = common_log_reslove_pb2.PubLogInfo()
    topicsmsg.ParseFromString(msg.data)
    for item in topicsmsg.topic_hz:
        topicInfo[item.name] = item.hz
        print item.name
        print item.hz    



def main():
    global brand
    global rosmachetype;
    if len(sys.argv) < 4:
        rospy.logerr("please use:system_guardian.py configfilename, rostopicfilename")
        exit(-1)
    rospy.init_node('system_guardian')
    #rosmachetype = rospy.get_param('rosmachetype')
    strFullParaName = "%s/rosmachetype" %(rospy.get_name())
    print("strFullParaName:%s" %strFullParaName)
    rosmachetype = rospy.get_param(strFullParaName)
    print("node_name:%s" %(rospy.get_name()))
    config_file = sys.argv[1].strip() #no use 
    rostopic_file = sys.argv[2].strip()
    brandtopicfile = sys.argv[3].strip()
    vehicleconfigfile = sys.argv[4].strip()
    brand = get_brand(vehicleconfigfile)

    rospy.Subscriber("/autopilot_info/internal/report_topic_hz", BinaryData, topics_callback)

    pth_topic = Thread(target=topicFun,args=(rostopic_file, brandtopicfile))
    print("pth:rostopic_file:%s"%rostopic_file)
    print("pth:brandtopicfile:%s"%brandtopicfile)
    print("pth:vehicleconfigfile:%s"%vehicleconfigfile)
    pth_topic.setDaemon(True)
    pth_topic.start()
    if rosmachetype == "master":
        p = Process(brandtopicfile)
        phard = guardian_hardware.Tail()
        guar_sub = Guardian_sub()
        guar_sub.rosslavesub()
       
        

    rospy.spin()

if __name__ == '__main__':
    try:
      
        main()
    except KeyboardInterrupt as e:
        print "user ctrl-c to exit"
        exit(0)
