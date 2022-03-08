#!/usr/bin/env python
from gc import collect
from pickle import FALSE
from re import S
from time import strftime, time, localtime
from rosnode import *
import psutil
from xml.dom.minidom import parse
import xml.dom.minidom
import rospy
import proto.vehicle_state_pb2
# from proto import chassis

abs_path = os.path.dirname(os.path.abspath(sys.argv[0]))
vehicle_path = os.path.abspath(abs_path + '/../config/vehicle')

def xml_parse(file,elem,attr):
    DOMTree = xml.dom.minidom.parse(file)
    collection = DOMTree.documentElement
    elems = collection.getElementsByTagName(elem)
    for e in elems:
        if e.hasAttribute(attr) and e.getAttribute(attr) == "device": 
            gnss_device = e.getAttribute("value")
    return os.path.exists(gnss_device)

def check_version():
    version_file = '/autocar-code/project_commit.txt'
    file_obj = open(version_file,'r')
    try:
        for line in file_obj.readlines():
            if line.find('Version:'):
                print(line)
                break
    except:
        pass
    file_obj.close()

def check_time():
    rest = FALSE
    curtime = strftime("%Y%m%d%H%M%S",localtime())
    filename = abs_path + '/launch_time'
    try:
        time_file = open(filename,'a+')
        time_file.seek(0)
        last_time = time_file.readline().strip()
        if not last_time:
            last_time = '20220222222222'
            time_file.write(last_time)
        if last_time >= curtime:
            print('time is too old')
            rest = False
        else:
            time_file.truncate(0)
            time_file.write(curtime)
            print("systime synchronization at %s"%curtime)
            rest = True
        # print(curtime)
    except:
        pass
    time_file.close()
    return rest

def check_gnss():
    gnss_device = ""
    DOMTree = xml.dom.minidom.parse(vehicle_path + '/drivers/gnss/gnss.launch')
    collection = DOMTree.documentElement
    params = collection.getElementsByTagName("param")
    for param in params:
        if param.hasAttribute("name") and param.getAttribute("name") == "device": 
            gnss_device = param.getAttribute("value")
            print(gnss_device)
    return os.path.exists(gnss_device)

def check_lidar():
    lidar_ip = []
    if os.environ('D_CAR_TYPE') == 'df' or os.environ('D_CAR_TYPE') == 'hq':
        lidar_ip.append('192.168.1.205')
    else:
        DOMTree = xml.dom.minidom.parse(vehicle_path + '/drivers/gnss/gnss.launch')
        collection = DOMTree.documentElement
        args = collection.getElementsByTagName("arg")
        for arg in args:
            if arg.hasAttribute("name") and arg.getAttribute("name") == "device_ip": 
                lidar_ip.append(arg.getAttribute("default"))
    for ip in lidar_ip:
        if os.system('ping -c 2 -W 2 %s'%ip) != 0:
            print("cannot connect with lidar ip:%s"%ip)
            return False
    return True

def check_pad_connection():
    for session in psutil.net_connections(kind="tcp"):
        if session.laddr and session.raddr:
            if session.laddr.port == 4110 and session.status == psutil.CONN_ESTABLISHED:
                return True
    return False

def check_nodes():
    rest = True
    master = rosgraph.Master(ID)
    try:
        state = master.getSystemState()
    except socket.error:
        raise ROSNodeIOException("Unable to communicate with master!")

    nodes = []
    for s in state:
        for t, l in s:
            nodes.extend(l)
    nodes = list(set(nodes)) #uniq
    unpinged = []
    for node in nodes:
        if str(node).find("rostopic") == -1 and not rosnode_ping(node, max_count=1, verbose=False, skip_cache=False) :
            unpinged.append(node)
            print("%s has crashed"%node)
    return rest  

def check_gear():
    pass

def checkall():
    pass

def diagnose():
    pass

sys.exit(check_gear())