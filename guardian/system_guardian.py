#! coding=utf-8
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

def main():
    if len(sys.argv) < 2:
        rospy.logerr("please use:system_guardian.py filename")
        exit(-1)
    rospy.init_node('system_guardian')
    config_file = sys.argv[1].strip()
    print (config_file)
    p = Process(config_file)
    rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print "user ctrl-c to exit"
        exit(0)
