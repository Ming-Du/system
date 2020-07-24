#! coding=utf-8
import rospy
import rosnode
import rosparam
import os
from threading import Thread

class Process(Thread):
  NodeList=[]
  ParamName='isReady'
  
  def __init__(self):
    Thread.__init__(self)
    self.daemon = True
    self.register()
    self.start()
    
  def run(self):
  
    while True:
      #node_list = [ node for node in rosnode.get_node_names() if node not in '/rosout' ]
      ps_num = 0
      
      for node_name in self.NodeList:
        pid = os.popen("ps -ef | grep __name:=" 
          + node_name 
          + " | grep -v 'grep' | awk '{print $2}'").read()
          
        if len(pid) is 0: 
          rospy.logerr(node_name + " is off")
        else:
          rospy.loginfo(node_name + " on, pid: " + pid[:-1]) # 换行符
          ps_num += 1
        
      if ps_num is len(self.NodeList):
        rospy.logwarn('system is ok')
        rosparam.set_param(self.ParamName, '1')
      else:
        rosparam.set_param(self.ParamName, '0')
        
      print('---------')
      rospy.sleep(2)
      
  def register(self):
    # drivers
    self.NodeList.append('drivers_camera')
    self.NodeList.append('drivers_gnss')
    self.NodeList.append('drivers_lslidar_c32_driver')
    self.NodeList.append('drivers_lslidar_c32_decoder')
    self.NodeList.append('drivers_lslidar_c16_driver_left')
    self.NodeList.append('drivers_lslidar_c16_decoder_left')
    self.NodeList.append('drivers_lslidar_c16_driver_right')
    self.NodeList.append('drivers_lslidar_c16_decoder_right')
    # perception
    self.NodeList.append('perception_camera_detection')
    self.NodeList.append('perception_lidar_front')
    #self.NodeList.append('perception_lidar_front_left')
    #self.NodeList.append('perception_lidar_front_right')
    
    # telematics
    self.NodeList.append('telematics');
    
    
    #self.NodeList.append('system_guardian')


if __name__ == '__main__':
  rospy.init_node('system_guardian')
  p = Process()

  rospy.spin()
