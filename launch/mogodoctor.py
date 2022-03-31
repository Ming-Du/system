#!/usr/bin/env python
#--coding:utf-8

import os, sys
import json
import re
import logging
logging.basicConfig()
from math import modf
from time import strftime, time, localtime
import psutil
import xml.dom.minidom
import rospy
from rospy import Subscriber, logerr_once, loginfo, logerr, logwarn
from rosnode import *
from rostopic import msgevalgen, get_topic_class, genpy
import rospkg
try:
    from common import vehicle_state_pb2 as vehicle_state
    from common.vehicle_state_pb2 import VehicleState
    from common import control_command_pb2 as control_command
except:
    sys.path.append(rospkg.RosPack().get_path('operator_tool') + '/proto')
    import vehicle_state_pb2 as vehicle_state
    from vehicle_state_pb2 import VehicleState
    import control_command_pb2 as control_command
from std_msgs.msg import Float64MultiArray

from autopilot_msgs.msg import BinaryData
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
        
class TopicCallback(object):
    """
    Callback instance that can print callback data in a variety of
    formats. Used for all variants of rostopic echo
    """

    def __init__(self, topic, proto_type=None, msg_eval=None):
        __slots__ = ('topic', 'proto_type', 'msg_eval', 'done',
                     'count', 'stat', 'last_topic', 'last_msg_eval', 'protobuf')
        if topic and topic[-1] == '/':
            topic = topic[:-1]
        self.topic = topic
        self.proto_type = proto_type
        self.msg_eval = msg_eval

        # done tracks when we've exceeded the count
        self.done = False
        self.count = 0

        self.stat = False

        # cache
        self.last_topic = None
        self.last_msg_eval = None

        # proto data
        self.protobuf = None

    def custom_strify_message(self, val, indent='', time_offset=None, current_time=None, field_filter=None,
                              type_information=None, fixed_numeric_width=None, value_transform=None):
        # ensure to print uint8[] as array of numbers instead of string
        if type_information and type_information.startswith('uint8['):
            val = [ord(x) for x in val]
        if value_transform is not None:
            val = value_transform(val, type_information)
        return genpy.message.strify_message(val, indent=indent, time_offset=time_offset, current_time=current_time, field_filter=field_filter, fixed_numeric_width=fixed_numeric_width)

    def callback(self, data, callback_args, current_time=None):
        """
        Callback to pass to rospy.Subscriber or to call
        manually. rospy.Subscriber constructor must also pass in the
        topic name as an additional arg
        :param data: Message
        :param topic: topic name, ``str``
        :param current_time: override calculation of current time, :class:`genpy.Time`
        """
        def _check_filed(msg, kvs):
            if msg is None:
                return False
            if len(kvs) == 0:
                return True
            if self.proto_type is not None:
                self.protobuf = self.proto_type()
                try:
                    if type(msg) == BinaryData:
                        self.protobuf.ParseFromString(msg.data)
                    else:
                        self.protobuf = msg
                except AttributeError:
                    logerr("%s has no attribute named data" % type(msg))
                    return False
            else:
                self.protobuf = msg
            
            for k in kvs:
                if hasattr(self.protobuf, k):
                    if kvs[k] is not None and self.protobuf.__getattribute__(k) != kvs[k]:
                        return False
                    else:
                        return True
                else:
                    return False
            # if hasattr(self.protobuf, k):
            #     if v is not None and self.protobuf.__getattribute__(k) != v:
            #         return False
            #     else:
            #         return True
            # else:
            #     return False
        try:
            topic = callback_args['topic']
            fileds = callback_args['fileds'] #dict
        except:
            logerr("callback::key error")
            pass
        if self.count >= 1:
            self.done = True
            self.stat = _check_filed(data, fileds)
            return

        try:
            msg_eval = self.msg_eval
            if topic == self.topic:
                pass
            elif self.topic.startswith(topic + '/'):
                # self.topic is actually a reference to topic field, generate msgeval
                if topic == self.last_topic:
                    # use cached eval
                    msg_eval = self.last_msg_eval
                else:
                    # generate msg_eval and cache
                    self.last_msg_eval = msg_eval = msgevalgen(
                        self.topic[len(topic):])
                    self.last_topic = topic

            if msg_eval is not None:
                data = msg_eval(data)

            # data can be None if msg_eval returns None
            if data is not None:
                self.count += 1
                # handle data
                # TODO
            # #2778 : have to check count after incr to set done flag
            if self.count >= 1:
                self.done = True
                self.stat = _check_filed(data, fileds)

        except IOError:
            self.done = True
            self.stat = False
        except:
            # set done flag so we exit
            self.done = True
            self.stat = False

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

def check_version():
    version_file = '/autocar-code/project_commit.txt'
    version_info = ''
    try:
        with open(version_file, 'r') as file_obj:
            for line in file_obj.readlines():
                if line.find('Version:') != -1:
                    version_info = line.strip()
                    loginfo(version_info)
                    break
    except IOError:
        logerr("No version information,reason:no such file:%s"%version_file)
    return version_info

def check_time():
    rest = False
    curtime = strftime("%Y%m%d%H%M%S", localtime())
    filename = abs_path + '/launch_time'
    try:
        time_file = open(filename, 'a+')
        time_file.seek(0)
        last_time = time_file.readline().strip()
        if not last_time:
            last_time = '20220222222222'
            time_file.write(last_time)
        if last_time >= curtime:
            logerr('time is too old')
            rest = False
        else:
            time_file.truncate(0)
            time_file.write(curtime)
            loginfo("systime synchronization at %s" % curtime)
            rest = True
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
            loginfo("gnss device:%s" % gnss_device)
    return os.path.exists(gnss_device)

def check_lidar():
    lidar_ip = []
    car_type = None
    try:
        car_type = os.environ['D_CAR_TYPE']
    except KeyError:
        mogo_log("EINIT_BOOT","Environment[D_CAR_TYPE] not exist")
        logerr("Environment[D_CAR_TYPE] not exist")
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
        logerr("EHW_LIDAR","cannot get lidar ip")
        logerr("cannot get lidar ip")
    for ip in lidar_ip:
        if os.system('ping -c 2 -W 2 %s' % ip) != 0:
            mogo_log("EHW_LIDAR","cannot connect with lidar ip:%s" % ip)
            logerr("cannot connect with lidar ip:%s" % ip)
            return False
    return True

def check_pad_connection():
    for session in psutil.net_connections(kind="tcp"):
        if session.laddr and session.raddr:
            if session.laddr.port == 4110 and session.status == psutil.CONN_ESTABLISHED:
                return True
    return False

def check_pilotmode():
    mode = 0
    try:
        mode = rospy.get_param('/autopilot/PilotMode')
        if mode == 1:
            return True
        else:
            return False
    except KeyError:
        logerr("/autopilot/PilotMode has not been set")
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
    nodes = list(set(nodes))  # uniq
    unpinged = []
    for node in nodes:
        if str(node).find("rostopic") == -1 and not rosnode_ping(node, max_count=1, verbose=False, skip_cache=False):
            unpinged.append(node)
            mogo_log("EMAP_NODE","%s has crashed" % node)
            logerr("%s has crashed" % node)
    return rest

def check_topic(topic, classname=None, fileds={}):
    filed_data = {}
    if not topic:
        return (False, filed_data)
    c, s, m = get_topic_class(topic)
    if c is None or s is None:
        mogo_log("EMAP_TOPIC","%s has not been published yet" % topic)
        logerr("%s has not been published yet" % topic)
        return (False, filed_data)
    if s != topic:
        topic = s
    if not classname:
        classname = c

    topic_callback = TopicCallback(topic, proto_type=classname)
    topic_callback.msg_eval = m
    try:
        Subscriber(topic, c, topic_callback.callback, {
            'topic': topic, 'fileds': fileds})
    except:
        logerr("Subscribe %s failed" % topic)

    timeout_t = time.time() + 2.
    while time.time() < timeout_t and \
            topic_callback.count == 0 and \
            not rospy.is_shutdown() and \
            not topic_callback.done:
        rospy.rostime.wallsleep(0.2)
    if topic_callback.stat:
        loginfo("%s:%s"%(topic,topic_callback.protobuf))
        for filed in fileds:
            filed_data[filed] = topic_callback.protobuf.__getattribute__(filed)
    return (topic_callback.stat, filed_data)

def check_gear():
    (rest, data) = check_topic('/chassis/vehicle_state',
                               classname=vehicle_state.VehicleState, fileds={'gear':None})

    if rest == False:
        return -1
    else:
        return data['gear']

def check_global_trajectory():
    (rest, data) = check_topic('/planning/global_trajectory')
    return rest

def check_trajectory():
    (rest, data) = check_topic('/planning/trajectory')
    return rest

def check_leading_vehicle():
    (rest, data) = check_topic('/planning/leader',classname=Float64MultiArray,fileds={'data':None})
    if not rest:
        logerr("get /planning/leader topic error")
        return False
    if data["data"][1] < 5. :
        logwarn("distance with leading obstacle is less than 5m,maybe interfer autopilot")
        return False
    return True

def check_gps_stat():
    (rest, data) = check_topic('/sensor/gnss/gps_fix', fileds={'status':None})
    stat = data['status'].status
    if rest and stat == 42:
        return True
    mogo_log("EHW_RTK","gps status is abnormal:%s" % stat)
    logerr("gps status is abnormal:%s" % stat)
    return False

def check_can_stat():
    ip_cmd = "ip -d -s -h link show can0 | grep \"can state\" | awk '{print $3}'"
    can_state = _exec_cmd(ip_cmd)
    if can_state and can_state == 'BUS-OFF' : 
        return False 
    return True

def mdiff(func):
    import datetime
    def wrapper(*args,**kwargs):
        diff = time.time() - func(*args,**kwargs)
        return diff
    return wrapper

os.path.getmtime = mdiff(os.path.getmtime)

def check_telematics_log():
    def _transform_timestamp(stamp):
        if isinstance(stamp,int) or isinstance(stamp,float):
            return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(stamp))
        return '9999-99-99 99:99:99'
    def _split_lonlat(pos,n):
        dotpos = str(pos).find('.')
        if dotpos == -1:
            return str(pos)
        return str(pos)[:dotpos + n + 1]
    # logFile = 'log_'
    logFile = '/home/mogo/data/log/latest/telematics.launch.log'
    try:
        msec = os.path.getmtime(logFile)
        if msec > 5:
            logwarn("telematics' log has not updated for more than %s,make sure if telematics node has exit or restart by someone"%msec)
    except OSError:
        logerr("telematics' log not exist")
    ap_start_kw = r'APPstart.*\[1\]'
    ap_stop_kw = r'APPstart.*\[0\]'
    startLatLon_kw = r"APPstartAutoPilot:\s*startLatLon,\s*"
    endLatLon_kw = r"APPstartAutoPilot:\s*endLatLon,\s*"
    cmd = "sed -n -e '/%s/h' -e '/%s/H' -e '/%s/H' -e '/%s/H;${x;p}' %s"%(ap_start_kw,startLatLon_kw,endLatLon_kw,ap_stop_kw,logFile)
    cmd_stdout = _exec_cmd(cmd)
    if not cmd_stdout or cmd_stdout == '\n':
        logerr("telematics hasn't received autopilot command")
        return False,'',''
    
    mostp = re.findall(r'startLatLon,\s*lat:\s*\[(\d{2,3}\.\d*)?\]\s*lon:\s*\[(\d{2,3}\.\d*)\]',cmd_stdout)
    moedp = re.findall(r'endLatLon,\s*lat:\s*\[(\d{2,3}\.\d*)?\]\s*lon:\s*\[(\d{2,3}\.\d*)\]',cmd_stdout)
    stlat = stlon = edlat = edlon = 0.
    if len(mostp) > 0:
        stlat = float(mostp[0][0])
        stlon = float(mostp[0][1])
    if len(moedp) > 0:
        edlat = float(moedp[0][0])
        edlon = float(moedp[0][1])
    hadmap_engine_data_dir = rospkg.RosPack().get_path('hadmap_engine') + '/data/track_record_data/'
    posi_appendfix = _split_lonlat(stlon,5) + '_' + _split_lonlat(stlat,5) + '_' + _split_lonlat(edlon,5) + '_' + _split_lonlat(edlat,5)
    traj_filename =  hadmap_engine_data_dir + 'traj_' + posi_appendfix + '.csv'
    stop_filename=  hadmap_engine_data_dir + 'stop_' + posi_appendfix + '.txt'
    starttime = endtime = 0.
    for line in cmd_stdout.split('\n'):
        remod = re.findall(r'\[(\d*\.\d*)\]:\s*APPstartAutoPilot:\s*bEnable:\s*\[1\]',line)
        if len(remod) > 0: 
            starttime = float(remod[0])
            continue
        remod = re.findall(r'\[(\d*\.\d*)\]:\s*APPstartAutoPilot:\s*bEnable:\s*\[0\]',line)
        if len(remod) > 0: 
            endtime = float(remod[0])
    loginfo("traj:%s\nstop:%s"%(traj_filename,stop_filename))
    if int(endtime) > 0:
        mogo_log("IMAP_START_TIME","autopilot has exit by user request.start time:%s, end time:%s"%(_transform_timestamp(starttime),_transform_timestamp(endtime)))
        logerr("autopilot has exit by user request.start time:%s, end time:%s"%(_transform_timestamp(starttime),_transform_timestamp(endtime)))
        return False,traj_filename,stop_filename
    else:
        # 获取起点终点坐标
        mogo_log("IMAP_START_TIME","receive autopilot at %s"%_transform_timestamp(starttime))
        loginfo("receive autopilot at %s"%_transform_timestamp(starttime))
        return True,traj_filename,stop_filename

def check_traj_file(traj_filename,stop_filename):
    if not traj_filename or not stop_filename:
        logerr("files' name is empty")
        return False
    if os.access(traj_filename,os.R_OK) and os.access(stop_filename,os.R_OK):
        return True
    else:
        mogo_log("EMAP_TRA","trajectory file not exist or cannot be read,maybe use hadmap_engine to generate trajectory")
        mogo_log("IMAP_STYLE_TRACKING","generate trajectory")
        logwarn("trajectory file not exist or cannot be read,maybe use hadmap_engine to generate trajectory")
        return False

def check_control_command():
    return check_topic("/chassis/command",classname=control_command.ControlCommand,fileds={'pilot_mode':None,'trajectory_missing':None,'chassis_status_missing':None})

def check_can_node():
    can_launch_dict = {'df':'DongFeng_E70_can_adapter.launch',
                       'jinlv':'jinlv_can_adapter.launch',
                       'hq':'Hongqi_H9_can_adapter.launch',
                       'byd':'byd_can_adapter.launch',
                       'wey':'vv6_can_adapter.launch'}
    ns = '/'
    can_node = ''
    # can_pkg_launch_file = rospkg.RosPack().get_path('can_adapter') + '/launch/'
    os.environ['D_CAR_TYPE'] = os.environ.get('D_CAR_TYPE',_get_car_type())
    launch_can = rospkg.RosPack().get_path('launch') + '/can_adapter.launch'
    can_adapter_can = rospkg.RosPack().get_path('can_adapter') + '/launch/' + can_launch_dict[os.environ['D_CAR_TYPE']]
    if os.access(launch_can,os.R_OK):
        can_pkg_launch_file = launch_can
    else:
        can_pkg_launch_file = can_adapter_can
    for file in _get_file_list([can_pkg_launch_file]):
        DOMTree = xml.dom.minidom.parse(file)
        collection = DOMTree.documentElement
        nodes = collection.getElementsByTagName("node")
        for node in nodes:
            if node.hasAttribute("ns") :
                ns += node.getAttribute("ns") 
            if node.hasAttribute("name") :
                can_node = ns + node.getAttribute("name") 
            elif node.getAttribute("type"):
                can_node = ns + node.getAttribute("type")
            
            if can_node:
                loginfo("can node is %s"%can_node)
                if rosnode_ping(can_node, max_count=1, verbose=False, skip_cache=False):
                    return True
                else:
                    mogo_log("EMAP_NODE","can_adapter node has exit")
                    logerr("can_adapter node has exit")
                    return False
            else:
                continue
    return False

def check_vehicle_stat():
    return check_topic("/vehicle/status/panel",classname=vehicle_state.VehicleState,fileds={'pilot_mode':None,'longitude_driving_mode':None,'eps_steering_mode':None})

def checkall():
    ver = check_version()
    if ver != '':
        mogo_log("IINIT_VERSION",ver)
    if not check_gnss():
        mogo_log("EHW_GNSS","gnss device doesn't exist")
    else:
        mogo_log("IINIT_SENSOR_NORMAL","gnss device is normal")
    if not check_lidar():
        mogo_log("EHW_LIDAR","cannot communicate with lidar")
    else:
        mogo_log("IINIT_SENSOR_NORMAL","connected with lidar successfully")

def diagnose():
    check_version()
    traj_file = ''
    stop_file = ''
    if not check_pad_connection():
        mogo_log("EHW_NET","Pad hasn't connected with telematics")
        logerr("Pad hasn't connected with telematics")
        return -1
    (status,traj_file,stop_file) = check_telematics_log()
    if not status:#没收到pad指令或已经退出自动驾驶
        return 0
    if not check_pilotmode():# 收到人工接管指令，但驾驶状态没变
        rest = check_gear()
        if rest == -1 and not check_can_node():
            #check can_adapter node
            return -1
        elif rest == 0:
            if not check_can_stat():
                mogo_log("EHW_CAN","can0 state[BUS-OFF],cannot receive chassis information")
                logerr("can0 state[BUS-OFF],cannot receive chassis information")
                return -3
        elif rest == 2 or rest == 3:
            gear_des = {0: "NONE", 1: "N", 2: "R", 3: "P", 4: "D"}
            mogo_log("EVHC_GEAR","current gear[%s] is not 'N' or 'D',cannot enter autopilot"%gear_des[rest])
            logerr("current gear[%s] is not 'N' or 'D',cannot enter autopilot"%gear_des[rest])
            return -4
    if status:            
        check_traj_file(traj_file,stop_file)
    if not check_nodes():
        return -1
    if not check_global_trajectory():
        if not check_gps_stat():
            return -7
        mogo_log("EMAP_TOPIC","/planning/global_trajectroy topic has no message")
        logerr("/planning/global_trajectroy topic has no message")
        return -6
    if not check_trajectory():
        mogo_log("EMAP_TOPIC","/planning/trajectroy topic has no message")
        logerr("/planning/trajectroy topic has no message")
        return -6
    
    # check leading obstacle
    check_leading_vehicle()
    # check control_command
    status,data = check_control_command()
    if status:
        loginfo(data)
        mogo_log("IMAP_CONTROL_COMMAND","autopilot command to vehicle is %s"%data['pilot_mode'])
        loginfo("autopilot command to vehicle is %s"%data['pilot_mode'])
        if data['pilot_mode'] == 0:
            mogo_log("EMAP_TOPIC","command to vehicle is manul mode")
            logerr("command to vehicle is manul mode")
            return -6
    else:
        mogo_log("EMAP_TOPIC","control node doesn't send command to chassis")
        logerr("control node doesn't send command to chassis")
        return -8
    # check vehicle_stat
    status,data = check_vehicle_stat()
    if status:
        mogo_log("IMAP_CHASSIS_STATUS","pilot_mode:%s,longitude_driving_mode:%s,eps_steering_mode:%s"%(data['pilot_mode'],data['longitude_driving_mode'],data['eps_steering_mode']))
        loginfo("pilot_mode:%s    longitude_driving_mode:%s    eps_steering_mode:%s"%(data['pilot_mode'],data['longitude_driving_mode'],data['eps_steering_mode']))
        if data['pilot_mode'] == 0:
            mogo_log("EVHC_CSS","control send command to vehicle but vehicle didn't enter to autopilot")
            logerr("control send command to vehicle but vehicle didn't enter to autopilot")
            if data['eps_steering_mode'] != 0:logwarn("eps_steering_mode is auto mode[%s],check if vehicle have warnnings"%data['eps_steering_mode'])
            if data['longitude_driving_mode'] != 0:logwarn("longitude_driving_mode is auto mode[%s],check if vehicle have warnnings"%data['longitude_driving_mode'])
        else:
            loginfo("pilot mode of chassis is autopilot")
    return 0

def sig_handler():
    loginfo("shut down")
    if file_stat:f_msg_obj.close()
if __name__ == '__main__':
    rospy.on_shutdown(sig_handler)
    file_stat = False
    opt = []
    act_check = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'c': act_check = True
    msg_config = None
    try:
        with open(config_path + '/mogo_report_msg.json','r') as msg:
            no_act_res_config = json.load(msg)
    except IOError as e:
        no_act_res_config = {}
        logerr("open %s/mogo_report_msg.json failed:%s"%(config_path,e.strerror))
    
    try:
        f_msg_obj = open('/home/mogo/data/log/msg_log/mogodoctor_report.json',"a+")
        file_stat = True
    except IOError as e:
        logerr("open mogodoctor_report.json failed:%s"%e.strerror)
        
    if act_check:
        checkall()
        if file_stat:f_msg_obj.close()
        sys.exit(0)

    rospy.init_node('mogodoctor',anonymous=True)
    rate = rospy.Rate(0.5)
    while not rospy.is_shutdown():
        diagnose()
        rate.sleep()
    rospy.spin()
    sys.exit(0)
