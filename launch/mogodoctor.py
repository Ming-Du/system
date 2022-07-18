#!/usr/bin/env python
#--coding:utf-8

import os, sys
import socket
import json
import re
import logging
logging.basicConfig()
from math import modf
from time import time
import psutil
import xml.dom.minidom
try:
    from roslaunch.mogo_msg import MOGO_MSG
except:
    pass
from rospy import logerr_once, loginfo, logerr, logwarn
from rosnode import *
import rospkg

# from proto import chassis
global f_msg_obj
global file_stat
global no_act_res_config
abs_path = os.path.dirname(os.path.abspath(sys.argv[0]))
config_path = rospkg.RosPack().get_path('config')
vehicle_path = config_path + '/vehicle'

def mogo_log(no, msg):
    if not file_stat:
        logerr_once("cannot write mogo msg to report")
        return
    # {\"timestamp\": {\"sec\": $(date +"%s"), \"nsec\": $(date +"%N")}, \"src\": \"$this\", $append, \"msg\": \"$msg\"}
    msg_obj = no_act_res_config.get(no)
    if not msg_obj:
        msg_obj = {}
    (ns,s) = modf(time.time())
    timestamp = {"sec":int(s),"nsec":int(ns * 1e9)}
    msg_obj["timestamp"] = timestamp
    msg_obj["src"] = sys.argv[0]
    msg_obj["msg"] = msg
    json.dump(msg_obj,f_msg_obj)
    f_msg_obj.write("\n")

def _get_car_type():
    try:
        with open(vehicle_path + '/vehicle_config.txt','r') as f:
            for line in f.readlines():
                if line.find('brand') != -1 :
                    mo = re.search(r'\".*\"',line)
                    if not mo:
                        logerr("vehicle_config.txt has no item named brand")
                        return ''
                    if mo.group() == "\"DF\"" : return 'df'
                    elif mo.group() == "\"JINLV\"" : return 'jinlv'
                    elif mo.group() == "\"HQ\"" : return 'hq'
                    elif mo.group() == "\"BYD\"" : return 'byd'
                    elif mo.group() == "\"WEY\"" : return 'wey'
    except IOError:
        logerr("No such file or directory:%s"%(vehicle_path + '/vehicle_config.txt'))
        
def _exec_cmd(cmd):
        try:
            handle = os.popen(cmd)
            rest = handle.read()
            handle.close()
            return rest
        except:
            logerr("exec system command failed:%s"%cmd)
            raise IOError

def _get_file_list(roslaunch_files):
    """
    :param roslaunch_files: list of launch files to load, ``str``

    :returns: list of files involved in processing roslaunch_files, including the files themselves.
    """
    from roslaunch.config import load_config_default, get_roscore_filename
    import roslaunch.xmlloader
    try:
        loader = roslaunch.xmlloader.XmlLoader(resolve_anon=True)
        config = load_config_default(
            roslaunch_files, None, loader=loader, verbose=False, assign_machines=False)
        files = [os.path.abspath(x) for x in set(
            config.roslaunch_files) - set([get_roscore_filename()])]
        return files
    except roslaunch.core.RLException as e:
        logerr(str(e))

def xml_parse(file, elem, attr):
    DOMTree = xml.dom.minidom.parse(file)
    collection = DOMTree.documentElement
    elems = collection.getElementsByTagName(elem)
    for e in elems:
        if e.hasAttribute(attr) and e.getAttribute(attr) == "device":
            gnss_device = e.getAttribute("value")
    return os.path.exists(gnss_device)


def check_gnss():
    gnss_device = ""
    DOMTree = xml.dom.minidom.parse(vehicle_path + '/drivers/gnss/gnss.launch')
    collection = DOMTree.documentElement
    params = collection.getElementsByTagName("param")
    for param in params:
        if param.hasAttribute("name") and param.getAttribute("name") == "device":
            gnss_device = param.getAttribute("value")
            loginfo("gnss device:%s" % gnss_device)
    if os.path.exists(gnss_device):
        mogo_logger.mogo_write("IINIT_SENSOR_NORMAL","gnss device is normal")
    else:
        mogo_logger.mogo_write("EHW_GNSS","gnss device doesn't exist")


def check_lidar():
    global mogo_logger
    lidar_ip = []
    car_type = os.environ.get('D_CAR_TYPE')
    if car_type == 'df' or car_type == 'hq':
        lidar_ip.append('192.168.1.205')
    else:
        for launch_file in _get_file_list([vehicle_path + '/drivers/lidar/lidar.launch']):
            DOMTree = xml.dom.minidom.parse(launch_file)
            collection = DOMTree.documentElement
            args = collection.getElementsByTagName("arg")
            for arg in args:
                if arg.hasAttribute("name") and arg.getAttribute("name") == "device_ip":
                    lidar_ip.append(arg.getAttribute("default"))

    if len(lidar_ip) == 0:
        mogo_logger.mogo_write("EHW_LIDAR","cannot get lidar ip")
        logerr("cannot get lidar ip")
    
    err_num = 0
    for ip in lidar_ip:
        if os.system('ping -c 2 -W 2 %s >/dev/null 2>&1'%ip) != 0:
            mogo_logger.mogo_write("EHW_LIDAR","cannot connect with lidar ip:%s" % ip)
            logerr("cannot connect with lidar ip:%s" % ip)
            err_num += 1
            mogo_logger.mogo_write("EHW_LIDAR","cannot communicate with lidar")
    if err_num == 0:
        mogo_logger.mogo_write("IINIT_SENSOR_NORMAL","connected with lidar successfully")

def mdiff(func):
    import datetime
    def wrapper(*args,**kwargs):
        diff = time.time() - func(*args,**kwargs)
        return diff
    return wrapper

def checkall():
    hostname = os.environ.get('ROS_HOSTNAME')
    master_uri = os.environ.get('ROS_MASTER_URI')
    master = master_uri.split(':')[1].split('//')[1]
    socket.getaddrinfo
    if master and master == hostname:
        check_gnss()
        check_lidar()

def sig_handler():
    loginfo("shut down")
    if file_stat:f_msg_obj.close()

def main():
    global mogo_logger
    HOST = socket.gethostbyname(os.environ.get('ROS_HOSTNAME'))
    if not HOST:
        HOST = socket.gethostbyname(socket.gethostname())
    mogo_logger = MOGO_MSG(ID="[%s] roslaunch"%HOST,logdir=rospkg.get_log_dir())
    mogo_logger.init()
    checkall()

if __name__ == '__main__':
    main()