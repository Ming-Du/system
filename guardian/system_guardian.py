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

class Process(Thread):
  NodeList=[]
  ParamName='/system/isReady'  #logDetail
  node_state_dict={}
  
  def __init__(self):
    Thread.__init__(self)
    self.daemon = True
    self.register()
    self.start()
    
  def run(self):
    pub_node = rospy.Publisher('/system/nodes',String, queue_size=100)
    pub_cpu = rospy.Publisher('/system/cpu',String, queue_size=100)
    pub_mem = rospy.Publisher('/system/mem',String, queue_size=100)
    
    rate = rospy.Rate(1)
    while True:
      #node_list = [ node for node in rosnode.get_node_names() if node not in '/rosout' ]
      ps_num = 0
      self.node_state_dict = {}
      
      for node_name in self.NodeList:
        pid = os.popen("ps -ef | grep __name:=" 
          + node_name 
          + " | grep -v 'grep' | awk '{print $2}'").read()
          
        if len(pid) is 0: 
          rospy.logerr(node_name + " is off, trying to restart...")
          self.start_node(node_name)
          self.node_state_dict[node_name] = "off"
        else:
          rospy.loginfo(node_name + " on, pid: " + pid[:-1]) 
          ps_num += 1
          self.node_state_dict[node_name] = "on"
        
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
    self.NodeList.append('drivers_camera')
    self.NodeList.append('drivers_gnss')
    self.NodeList.append('drivers_lidar32_front_driver')
    self.NodeList.append('drivers_lidar32_front_decoder')
    self.NodeList.append('drivers_lidar16_left_driver')
    self.NodeList.append('drivers_lidar16_left_decoder')
    self.NodeList.append('drivers_lidar16_right_driver')
    self.NodeList.append('drivers_lidar16_right_decoder')
    # perception
    self.NodeList.append('perception_camera_detection')
    self.NodeList.append('perception_lidar32_front')
    self.NodeList.append('perception_lidar16_front_left')
    self.NodeList.append('perception_lidar16_front_right')
    
    # telematics
    #self.NodeList.append('telematics');
    
    #self.NodeList.append('system_guardian')
    #rospy.Subscriber("/sensor/gnss/gps_fix")
    #if (status.status == 2) is fine


if __name__ == '__main__':
    rospy.init_node('system_guardian')
    p = Process()
    rospy.spin()
