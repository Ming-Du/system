#!/usr/bin/env python
# -*- coding: utf-8 -*-

###### python
import os
import os.path
import sys
import signal
import time
import json
#import psutil
import subprocess

###### ros module
import rospy
import rostopic
import rosgraph
import roslaunch
import rosnode
import rosservice
from std_msgs.msg import String, UInt8, Int32
from rospy import init_node, Subscriber, Publisher
from rospy import rostime

###### pyqt
from python_qt_binding import loadUi
from PyQt5.QtCore import QStringListModel, QAbstractListModel, QModelIndex, QSize
from PyQt5.QtWidgets import QMessageBox, QListWidgetItem
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QThread, pyqtSignal

###### mogo
#import proto
from proto import *
from autopilot_msgs.msg import BinaryData

#######
USE_QT4 = True

## ros will add 2 more params after your params
if len(sys.argv) < 2:
    print("==============================================================")
    print("Usage:")
    print(" python operator_tool.py qt5")
    print("\n")
    print("Example:")
    print(" python operator_tool.py qt5")
    print("==============================================================")
    exit()
else:
    if sys.argv[1] == "qt5":
        USE_QT4 = False

if USE_QT4:
    from PyQt4 import QtGui
    from PyQt4 import QtCore
    from PyQt4.QtCore import pyqtSlot
    Widget = QtGui.QWidget
    Application = QtGui.QApplication
else:  # Qt5
    from PyQt5 import QtGui
    from PyQt5 import QtCore, QtWidgets
    from PyQt5.QtCore import pyqtSlot
    Widget = QtWidgets.QWidget
    Application = QtWidgets.QApplication

# PilotMode(Enum):
AutoMode  = 1
HumanMode = 0
Pre_mode  = 1
_count_ = 0
AutoPilotModeBtnClicked = HumanMode

# LaneChange(Enum):
Keep = 0
# CtrlLight(Enum):
Release = 0
Left = 1
Right = 2
Flash = 3

# CtrlMode(Enum):
Human = 0
Keyboad = 2
Param = 3
Auto = 4

GreenLight = 2
RedLight = 1
Release = 0

## thread class 
class toolThread(QThread):
    update_sts = pyqtSignal(list)
    def __init__(self, topic, msg_type, call_back, parent=None):
        super(toolThread, self).__init__(parent)
        rospy.Subscriber(topic, msg_type, call_back)
    def run(self):
        rospy.spin()

## position, used by mark map.call back funtion.
MarkMapPosition_x = 0.0
MarkMapPosition_y = 0.0
MarkMapPosition_longitude = 0.0
MarkMapPosition_latitude  = 0.0

def recvGlobalLocation(ros_msg):
    location = common_localization.Localization()
    location.ParseFromString(ros_msg.data)
    global MarkMapPosition_x
    global MarkMapPosition_y
    global MarkMapPosition_longitude
    global MarkMapPosition_latitude
    MarkMapPosition_x = location.position.x
    MarkMapPosition_y = location.position.y
    MarkMapPosition_longitude = location.longitude
    MarkMapPosition_latitude  = location.latitude
    print (MarkMapPosition_x)
    print (MarkMapPosition_y)
    print (MarkMapPosition_longitude)
    print (MarkMapPosition_latitude)

## ros gardian thread call back funtion
g_ros_gardian_msg_dict = {}
def recvGardianMsg(ros_msg):
    global g_ros_gardian_msg_dict
    ros_msg_str = str(ros_msg.data)
    g_ros_gardian_msg_dict = json.loads(ros_msg_str)

## ros mem thread call back function
g_ros_mem_msg_dict = {}
def recvMemMsg(ros_msg):
    global g_ros_mem_msg_dict
    ros_msg_str = str(ros_msg.data)
    g_ros_mem_msg_dict = json.loads(ros_msg_str)

## ros cpu thread call back funtion
g_ros_cpu_msg_dict = {}
def recvCpuMsg(ros_msg):
    global g_ros_cpu_msg_dict
    ros_msg_str = str(ros_msg.data)
    #print(repr(ros_msg_str))
    g_ros_cpu_msg_dict = json.loads(ros_msg_str)
 
## ros vehicle state thread call back function
g_vstate_brake_pre    = -1
g_vstate_throttle_pre = -1
g_vstate_brake        = -1
g_vstate_throttle     = -1 
g_longitude_driving_mode = -1
g_longitude_driving_mode_pre = -1
g_brake_secs         = 0
g_pilot_mode         = 0
g_pilot_mode_pre     = 0

def recv_vstatus(ros_msg):
    #global  g_vehicle_state
    g_vehicle_state = common_vehicle_state.VehicleState()
    g_vehicle_state.ParseFromString(ros_msg.data)
    global g_vstate_brake
    global g_vstate_throttle
    global g_longitude_driving_mode
    global g_pilot_mode
    g_vstate_brake    = g_vehicle_state.brake
    g_vstate_throttle = g_vehicle_state.throttle
    g_longitude_driving_mode = g_vehicle_state.longitude_driving_mode
    g_pilot_mode = g_vehicle_state.pilot_mode

## /system/rostopics thread call back function
g_ros_hz_msg_dict = {}
def recvHzMsg(ros_msg):
    global g_ros_hz_msg_dict
    ros_msg_str = str(ros_msg.data)
    g_ros_hz_msg_dict = json.loads(ros_msg_str)

#########################################
class MyApp(Widget):
    def __init__(self):
        super(MyApp, self).__init__()
        self_dir = os.path.dirname(os.path.realpath(__file__))
        self.ui_dir = self_dir
        ui_file = os.path.join(self.ui_dir, 'operator_tool.ui')
        loadUi(ui_file, self)
        self.setWindowTitle('Operator Tool')
        rospy.init_node('operator_tool')

        ## topic publishers
        self.lock_log_pub = Publisher('/system/LockLog', Int32, queue_size=10)
        self.set_map_pub  = Publisher('/hadmap/routing_requests', BinaryData, queue_size=10)

        ## init some params
        rospy.set_param("/autopilot/PilotMode", HumanMode)
        rospy.set_param("/autopilot/TrafficLightCmd", Release)

        # init track record info
        self.textBroswer_track_file.setText("")
        self.record_track_log_file = ""

        ## init some log dirs
        self.initTrackAndMarkMapFilePath()

        ## init mark map info
        self.home_path = os.path.expanduser('~')
        self.mark_map_file_name = ""
        self.mark_map_file_fd = None
        self.speed_limit_num = 0
        self.stop_cross_walk = 0
        self.stop_line = 0

        ## status info
        self.cpu_status_info = ""
        self.mem_status_info = ""
        self.ros_node_info   = ""
        self.veh_status_info = ""

        #### init choose map
        self.choose_map_file_dict = None
        self.set_choose_map_file  = ""
        self.choose_map_dict = {}
        self.map_total = {}

        ## init module event
        self.set_module_event()

        ### set event loop
        self.set_timer_event()

        ## enable the btns
        self.set_forPlan_enable(True)

        ## mark lidar
        self.ros_service_name = "" 
        self.initComboBoxLidarServices()

        ### threads
        self.startThreads()

    ## start some threads
    def startThreads(self):
        self.location_thread = toolThread('/localization/global', BinaryData, recvGlobalLocation)
        self.location_thread.start()

        self.gardian_thread = toolThread('/system/nodes', String, recvGardianMsg)
        self.gardian_thread.start()

        self.cpu_thread = toolThread('/system/cpu', String, recvCpuMsg)
        self.cpu_thread.start()

        self.mem_thread = toolThread('/system/mem', String, recvMemMsg)
        self.mem_thread.start()

        self.hz_thread = toolThread('/system/rostopics', String, recvHzMsg)
        self.hz_thread.start()

        self.veh_state_thread = toolThread("/chassis/vehicle_state", BinaryData, recv_vstatus)
        self.veh_state_thread.start()

    ## check if traj_filter can find
    def checkTrajFilter(self):
        path_catkin_ws_install = "/home/mogo/catkin_ws/install/lib/hadmap/"
        path_catkin_ws_devel = "/home/mogo/catkin_ws/devel/lib/hadmap/"
        path_autopilot = "/home/mogo/autopilot/lib/hadmap/"
        
        #path_catkin_ws_install = "/home/yanggf/catkin_ws_dev/install/lib/hadmap/"
        #path_catkin_ws_devel = "/home/yanggf/catkin_ws_dev/devel/lib/hadmap/"
        #path_autopilot = "/home/yanggf/autopilot/lib/hadmap/"
    
        if os.path.isfile(path_catkin_ws_devel + "traj_filter") == True:
            self.traj_filter_exe_path = path_catkin_ws_devel
        elif os.path.isfile(path_catkin_ws_install + "traj_filter") == True:
            self.traj_filter_exe_path = path_catkin_ws_install
        elif os.path.isfile(path_autopilot + "traj_filter") == True:
            self.traj_filter_exe_path = path_autopilot
        else:
            msg_info = "Can not find traj_filter,start operator_tool fail."
            QMessageBox.warning(self,"Warning", msg_info, QMessageBox.Yes )
            return False
        return True

    ## check if track_recoder can find
    def checkTrackRecorder(self):
        path_catkin_ws_install = "/home/mogo/catkin_ws/install/lib/track_recorder/"
        path_catkin_ws_devel = "/home/mogo/catkin_ws/devel/lib/track_recorder/"
        path_autopilot = "/home/mogo/autopilot/lib/track_recorder/"
        
        #path_catkin_ws_install = "/home/yanggf/catkin_ws_dev/install/lib/track_recorder/"
        #path_catkin_ws_devel = "/home/yanggf/catkin_ws_dev/devel/lib/track_recorder/"
        #path_autopilot = "/home/yanggf/autopilot/lib/track_recorder/"

        if os.path.isfile(path_catkin_ws_install + "track_recorder") == True:
            return True
        elif os.path.isfile(path_catkin_ws_devel + "track_recorder") == True:
            return True
        elif os.path.isfile(path_autopilot + "track_recorder") == True:
            return True
        else:
            msg_info = "Can not find track_recorder,start operator_tool fail."
            QMessageBox.warning(self,"Warning", msg_info, QMessageBox.Yes )
            return False

    ## init log path
    def initTrackAndMarkMapFilePath(self):
        self.tool_log_path             = "/home/mogo/data/yun_ying/"
        #self.tool_log_path             = "/home/yanggf/yun_ying/"
        self.mark_map_file_path        = self.tool_log_path + "da_dian/"
        self.record_track_file_path    = self.tool_log_path + "gui_ji/"
        self.traj_file_path            = self.tool_log_path + "chou_xi/"
        self.map_file_path             = self.tool_log_path + "di_tu/"

        ## check parent path
        msg_info = ""
        if os.path.exists(self.tool_log_path) == False:
            print(self.tool_log_path + " do not exists,but I will create it.")
            os.makedirs(self.tool_log_path)
            if os.path.exists(self.tool_log_path) == False:
                msg_info = "Create " + self.tool_log_path + " fail."
                QMessageBox.warning(self,"Error", msg_info, QMessageBox.Yes )
                return

        ## create da dian file path
        if os.path.exists(self.mark_map_file_path) == False:
            print(self.mark_map_file_path + " do not exists,but I will create it.")
            os.makedirs(self.mark_map_file_path)
            if os.path.exists(self.mark_map_file_path) == False:
                msg_info = "Create " + self.mark_map_file_path + " fail."
                QMessageBox.warning(self,"Error", msg_info, QMessageBox.Yes )
                return
        
        ## create gui_ji file path
        if os.path.exists(self.record_track_file_path) == False:
            print(self.record_track_file_path + " do not exists,but I will create it.")
            os.makedirs(self.record_track_file_path)
            if os.path.exists(self.record_track_file_path) == False:
                msg_info = "Create " + self.record_track_file_path + " fail."
                QMessageBox.warning(self,"Error", msg_info, QMessageBox.Yes )
                return

        ## create chou xi file path
        if os.path.exists(self.traj_file_path) == False:
            print(self.traj_file_path + " do not exists,but I will create it.")
            os.makedirs(self.traj_file_path)
            if os.path.exists(self.traj_file_path) == False:
                msg_info = "Create " + self.traj_file_path + " fail."
                QMessageBox.warning(self,"Error", msg_info, QMessageBox.Yes )
                return
        
        ## create ditu file path
        if os.path.exists(self.map_file_path) == False:
            print(self.map_file_path + " do not exists,but I will create it.")
            os.makedirs(self.map_file_path)
            if os.path.exists(self.map_file_path) == False:
                msg_info = "Create " + self.map_file_path + " fail."
                QMessageBox.warning(self,"Error", msg_info, QMessageBox.Yes )
                return

    def set_module_event(self):
        self.btn_LaneChange_KeepLane.clicked.connect(
            lambda: self.btnSetLaneChange(self.btn_LaneChange_KeepLane, Keep))
        self.btn_LaneChange_Left.clicked.connect(
            lambda: self.btnSetLaneChange(self.btn_LaneChange_Left, Left))
        self.btn_LaneChange_Right.clicked.connect(
            lambda: self.btnSetLaneChange(self.btn_LaneChange_Right, Right))
        self.btn_plan_AutoMode.clicked.connect(
            lambda: self.btnSetPlanAutoMode(self.btn_plan_AutoMode, AutoMode))
        self.btn_plan_Human.clicked.connect(
            lambda: self.btnSetPlanAutoMode(self.btn_plan_Human, HumanMode))
        self.btn_plan_SetVelocity.clicked.connect(self.setPlanAimVelocity)

        ## traffic light
        self.btn_traffic_light_green.clicked.connect(
            lambda: self.btnSetTraffficLightState(self.btn_traffic_light_green, GreenLight))
        self.btn_traffic_light_red.clicked.connect(
            lambda: self.btnSetTraffficLightState(self.btn_traffic_light_red, RedLight))
        self.btn_traffic_light_release.clicked.connect(
            lambda: self.btnSetTraffficLightState(self.btn_traffic_light_release, Release))

        ## choose map
        self.btn_set_map.clicked.connect(self.btnChooseMapSetMap)
        self.btn_load_map.clicked.connect(self.btnLoadMap)
        self.comboBox_map_item.currentIndexChanged.connect(self.cbxChooseMapItem)
        self.comboBox_map_position.currentIndexChanged.connect(self.cbxChooseMapPosition)

        ## lock log
        self.btn_lock_log.clicked.connect(self.btnLockLog)

        ## record track
        self.btn_start_record_track.clicked.connect(self.btnStartRecordTrack)
        self.btn_stop_record_track.clicked.connect(self.btnStopRecordTrack)
        self.btn_track_file.clicked.connect(self.btnExportTrackFile)
        self.btn_load_track_file.clicked.connect(self.btnLoadTrackFile)

        ## mark map
        self.btn_release_mark_map_speed.clicked.connect(self.btnReleaseMarkMapSpeed)
        self.btn_mark_cross_walk_line.clicked.connect(self.btnMarkMapCrossWalkLine)
        self.btn_mark_stop_line_forward.clicked.connect(
            lambda: self.btnMarkMapStopLine(self.btn_mark_stop_line_forward))
        self.btn_mark_stop_line_turn_left.clicked.connect(
            lambda: self.btnMarkMapStopLine(self.btn_mark_stop_line_turn_left)) 
        self.btn_mark_stop_line_turn_right.clicked.connect(
            lambda: self.btnMarkMapStopLine(self.btn_mark_stop_line_turn_right))        
        self.btn_set_new_mark_map_file.clicked.connect(self.btnSetNewMarkMapFile)
    
        ## set speed limit
        self.btn_set_common_speed_limit.clicked.connect(
            lambda: self.btnSetCommonSpeedLimit(self.btn_set_common_speed_limit))
        self.btn_speed_limit_10.clicked.connect(
            lambda: self.btnSetCommonSpeedLimit(self.btn_speed_limit_10))
        self.btn_speed_limit_20.clicked.connect(
            lambda: self.btnSetCommonSpeedLimit(self.btn_speed_limit_20))
        self.btn_speed_limit_30.clicked.connect(
            lambda: self.btnSetCommonSpeedLimit(self.btn_speed_limit_30))
        self.btn_speed_limit_40.clicked.connect(
            lambda: self.btnSetCommonSpeedLimit(self.btn_speed_limit_40))

        ## build choose_map.json
        self.btn_set_choose_map_file_path.clicked.connect(self.btnSetChooseMapFilePath)
        self.btn_choose_traj_file.clicked.connect(self.btnChooseTrajFile)
        self.btn_choose_map_file.clicked.connect(self.btnChooseMapFile)
        self.btn_add_map.clicked.connect(self.btnAddMap)

        ## lidar
        self.btn_set_lidar_trans_and_rotate.clicked.connect(self.btnSetLidarTransAndRotate)
        self.comboBox_lidar_services.currentIndexChanged.connect(self.cbxChooseServiceItem)
        self.btn_refresh_ros_srv.clicked.connect(self.initComboBoxLidarServices)

    ## get all ros services
    def btnSetLidarTransAndRotate(self): 
        trans_x = self.spinbox_trans_x.value()
        trans_y = self.spinbox_trans_y.value()
        trans_z = self.spinbox_trans_z.value()
        rotate_x = self.spinbox_rotate_x.value()
        rotate_y = self.spinbox_rotate_y.value()
        rotate_z = self.spinbox_rotate_z.value()
        srv_cmd = "rosservice call " + self.ros_service_name + " "
        srv_cmd += "\"message: 'trans"
        srv_cmd += "{x," + str(trans_x) + ","
        srv_cmd += "y," + str(trans_y) + ","
        srv_cmd += "z," + str(trans_z) + "};"
        srv_cmd += "{x," + str(rotate_x) + ","
        srv_cmd += "y," + str(rotate_y) + ","
        srv_cmd += "z," + str(rotate_z) + "}'\""
        print(srv_cmd)
        os.system(srv_cmd)
        
    ## init lidar service combox
    def initComboBoxLidarServices(self):
        try:
            self.comboBox_lidar_services.clear()
            services_list = rosservice.get_service_list()
            services_list.sort()
            map_cnt = len(services_list)
            for i in range(map_cnt):
                self.comboBox_lidar_services.addItem(services_list[i])
        except:
            print("==============================================================")
            print("Init choose map combo box fail.")
            print("Please try to load choose map json file again.")
            print("==============================================================")

    ## choose service
    def cbxChooseServiceItem(self):
        try:
            self.ros_service_name = self.comboBox_lidar_services.currentText()
            print("service : " + self.ros_service_name)
        except:
            pass

    ## set max speed
    def setPlanAimVelocity(self):
        aim_vel = self.spinbox_aimVelocity.value()
        rospy.set_param("/autopilot/VelocityMax", round(int(aim_vel)/3.6, 2))

    ## load map dynamic
    def btnLoadMap(self):
        try:
            path = QtWidgets.QFileDialog.getOpenFileName(self,
                                                    "Load Map File", self.map_file_path)
            map_file = path[0]
            if len(map_file) == 0:
                return
            self.loadChooseMapFile(map_file)
            self.initChooseMapComboBox()
            self.initPositionComboBox()
        except:
            QMessageBox.information(self,"Error","Load map file fail.")

    ## load choose_map.json
    def loadChooseMapFile(self, choose_map_file):
        try:
            f = open(choose_map_file)
            self.choose_map_file_dict = json.load(f)
            f.close()
            map_dict = self.choose_map_file_dict["map"]
            map_cnt = len(map_dict)
            for i in range(map_cnt):
                map_info_dict    = {}
                traj_dict        = {}
                feature_map_dict = {}
                points_dict      = {}

                traj_dict["traj"] = map_dict[i]["traj"]
                feature_map_dict["feature_map"] = map_dict[i]["feature_map"]
                point_list_cnt = len(map_dict[i]["points"])
                for j in range(point_list_cnt):
                    point_dict = {}
                    point_dict["name"] = map_dict[i]["points"][j]["name"]
                    point_dict["x"]    = float(map_dict[i]["points"][j]["x"])
                    point_dict["y"]    = float(map_dict[i]["points"][j]["y"])
                    points_dict[point_dict["name"]] = point_dict
                map_info_dict["traj"]        = traj_dict
                map_info_dict["feature_map"] = feature_map_dict
                map_info_dict["points"] = points_dict
                self.choose_map_dict[map_dict[i]["name"]] = map_info_dict
        except:
            print("==============================================================")
            print("Load " + choose_map_file + " file fail.Please try again.")
            print("==============================================================")

    ## init choose map combobox
    def initChooseMapComboBox(self):
        try:
            self.comboBox_map_item.clear()
            map_dict = self.choose_map_file_dict["map"]
            map_cnt = len(map_dict)
            for i in range(map_cnt):
                self.comboBox_map_item.addItem(map_dict[i]["name"])
        except:
            print("==============================================================")
            print("Init choose map combo box fail.")
            print("Please try to load choose map json file again.")
            print("==============================================================")

    ## init position combobox
    def initPositionComboBox(self):
        try:
            self.comboBox_map_position.clear()
            map_name = self.choose_map_file_dict["map"][0]["name"]
            pos_list_dicts = self.choose_map_dict[map_name]["points"]
            pos_names      = pos_list_dicts.keys()
            for name in pos_names:
                self.comboBox_map_position.addItem(name)
        except:
            print("==============================================================")
            print("Init choose map position combo box fail.")
            print("Please try to load choose map json file again.")
            print("==============================================================")

    # todo more
    def cbxChooseMapItem(self):
        try:
            self.comboBox_map_position.clear()
            map_name = self.comboBox_map_item.currentText()
            pos_list_dicts = self.choose_map_dict[map_name]["points"]
            pos_names = pos_list_dicts.keys()
            for name in pos_names:
                self.comboBox_map_position.addItem(name)
        except:
            pass

    # todo more
    def cbxChooseMapPosition(self):
        position_name = self.comboBox_map_position.currentText()

    ## choose map action
    def btnChooseMapSetMap(self):
        click_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.textBrowser_set_map_time.setText(click_time)

        map_name        = self.comboBox_map_item.currentText()
        pos_name        = self.comboBox_map_position.currentText()
        set_map_msg     = self.buildRoutingMsg()
        set_map_msg_str = set_map_msg.SerializeToString()
        choose_map_data = BinaryData()
        choose_map_data.header.seq         = set_map_msg.header.seq
        choose_map_data.header.stamp.secs  = set_map_msg.header.stamp.sec
        choose_map_data.header.stamp.nsecs = set_map_msg.header.stamp.nsec
        choose_map_data.header.frame_id    = set_map_msg.header.frame_id
        choose_map_data.name               = "hadmap.RoutingRequest"
        choose_map_data.size               = len(set_map_msg_str)
        choose_map_data.data               = set_map_msg_str
        self.set_map_pub.publish(choose_map_data)
        print("===== Set Map Message to topic /hadmap/routing_requests ======")
        print(set_map_msg)
        print("==============================================================")

    ## build routing msg
    def buildRoutingMsg(self):
        map_name = self.comboBox_map_item.currentText()
        pos_name = self.comboBox_map_position.currentText()
        rout_msg                    = common_routing.RoutingRequest()
        rout_msg.header.seq         = 1
        rout_msg.header.stamp.sec   = rostime.Time.now().secs
        rout_msg.header.stamp.nsec  = rostime.Time.now().nsecs
        rout_msg.header.frame_id    = "operator_tool_frame_id"
        rout_msg.header.module_name = "operator_tool"
        
        rout_msg.map        = self.choose_map_dict[map_name]["traj"]["traj"]
        rout_msg.feature    = self.choose_map_dict[map_name]["feature_map"]["feature_map"]
        rout_msg.end.id     = pos_name
        rout_msg.end.s      = 1.0
        rout_msg.end.pose.x = float(self.choose_map_dict[map_name]["points"][pos_name]["x"])
        rout_msg.end.pose.y = float(self.choose_map_dict[map_name]["points"][pos_name]["y"])
        return rout_msg


    ## set mark map speed,for tool tab.
    def btnSetMarkMapSpeed(self, speed, info):
        speed_limit = speed / 3.6
        self.speed_limit_num += 1
        obj_str = "objects {" + "\n"
        obj_str += "text: \"SpeedLimit " + "#" + str(self.speed_limit_num) + "\"\n"
        obj_str += "type: OBJECT_TYPE_SpeedLimit" + "\n"
        obj_str += "value:" + str(speed_limit) + "\n"
        obj_str += "geom {" + "\n"
        obj_str += "x: " + str(MarkMapPosition_x) + "\n"
        obj_str += "y: " + str(MarkMapPosition_y) + "\n"
        obj_str += "}" + "\n"
        obj_str += "}" + "\n"
        obj_str += info
        try:
            self.mark_map_file_fd = open(self.mark_map_file_name, 'a')
            self.mark_map_file_fd.write(obj_str)
            self.mark_map_file_fd.flush()
            self.mark_map_file_fd.close()
            self.textBrowser_mark_map_status.setText(obj_str)
        except:
            pass

    #
    def btnReleaseMarkMapSpeed(self):
        speed_limit = -4.0
        self.speed_limit_num += 1
        obj_str = "objects {" + "\n"
        obj_str += "text: \"SpeedLimit " + "#" + str(self.speed_limit_num) + "\"\n"
        obj_str += "type: OBJECT_TYPE_SpeedLimit" + "\n"
        obj_str += "value:" + str(float(speed_limit)) + "\n"
        obj_str += "geom {" + "\n"
        obj_str += "x: " + str(MarkMapPosition_x) + "\n"
        obj_str += "y: " + str(MarkMapPosition_y) + "\n"
        obj_str += "}" + "\n"
        obj_str += "}" + "\n"
        try:
            self.mark_map_file_fd = open(self.mark_map_file_name, 'a')
            self.mark_map_file_fd.write(obj_str)
            self.mark_map_file_fd.flush()
            self.mark_map_file_fd.close()
            self.textBrowser_mark_map_status.setText(obj_str)
        except:
            pass

    ##
    def btnSetCommonSpeedLimit(self, btn):
        self.speed_limit_num += 1
        obj_str = "objects {" + "\n"
        obj_str += "text: \"SpeedLimit " + "#" + str(self.speed_limit_num) + "\"\n"
        obj_str += "type: OBJECT_TYPE_SpeedLimit" + "\n"
        
        if btn == self.btn_speed_limit_10:
            obj_str += "value:" + str(10 / 3.6) + "\n"
        elif btn == self.btn_speed_limit_20:
            obj_str += "value:" + str(20 / 3.6) + "\n"
        elif btn == self.btn_speed_limit_30:
            obj_str += "value:" + str(30 / 3.6) + "\n"
        elif btn == self.btn_speed_limit_40:
            obj_str += "value:" + str(40 / 3.6) + "\n"
        elif btn == self.btn_set_common_speed_limit:
            obj_str += "value:" + str(self.spinbox_common_speed_limit.value() / 3.6) + "\n"
        obj_str += "geom {" + "\n"
        obj_str += "x: " + str(MarkMapPosition_x) + "\n"
        obj_str += "y: " + str(MarkMapPosition_y) + "\n"
        obj_str += "}" + "\n"
        obj_str += "}" + "\n"
        try:
            self.mark_map_file_fd = open(self.mark_map_file_name, 'a')
            self.mark_map_file_fd.write(obj_str)
            self.mark_map_file_fd.flush()
            self.mark_map_file_fd.close()
            self.textBrowser_mark_map_status.setText(obj_str)
        except:
            pass

    ## mark stop line
    def btnMarkMapStopLine(self, btn):
        speed_limit = 0.0
        obj_str = "objects {" + "\n"
        self.stop_line += 1
        if btn == self.btn_mark_stop_line_forward:
            obj_str += "text: \"Stop " + "#" + str(self.stop_line) + " straight" + "\"\n"
            obj_str += "type: OBJECT_TYPE_Stop" + "\n"
            obj_str += "attribute: \"straight\"" + "\n"
            speed_limit = self.spinbox_straight_speed_limit.value()
        elif btn == self.btn_mark_stop_line_turn_left:
            obj_str += "text: \"Stop " + "#" + str(self.stop_line) + " left" + "\"\n"
            obj_str += "type: OBJECT_TYPE_Stop" + "\n"
            obj_str += "attribute: \"left\"" + "\n"
            speed_limit = self.spinbox_left_speed_limit.value()
        elif btn == self.btn_mark_stop_line_turn_right:
            obj_str += "text: \"Stop " + "#" + str(self.stop_line) + " right" + "\"\n"
            obj_str += "type: OBJECT_TYPE_Stop" + "\n"
            obj_str += "attribute: \"right\"" + "\n"
            speed_limit = self.spinbox_right_speed_limit.value()

        obj_str += "geom {" + "\n"
        obj_str += "x: " + str(MarkMapPosition_x) + "\n"
        obj_str += "y: " + str(MarkMapPosition_y) + "\n"
        obj_str += "}" + "\n"
        obj_str += "}" + "\n"
        try:
            self.mark_map_file_fd = open(self.mark_map_file_name, 'a')
            self.mark_map_file_fd.write(obj_str)
            self.mark_map_file_fd.flush()
            self.mark_map_file_fd.close()
            self.btnSetMarkMapSpeed(speed_limit, obj_str)
        except:
            print("write mark map info to file " + self.mark_map_file_name + " fail.")
            print("==============================================================")
            pass

    def btnMarkMapCrossWalkLine(self):
        self.stop_cross_walk += 1
        obj_str = "objects {" + "\n"
        obj_str += "text: \"Cross walk " + "#" + str(self.stop_cross_walk) + "\"\n"
        obj_str += "type: OBJECT_TYPE_CrossWalk" + "\n"
        obj_str += "geom {" + "\n"
        obj_str += "x: " + str(MarkMapPosition_x) + "\n"
        obj_str += "y: " + str(MarkMapPosition_y) + "\n"
        obj_str += "}" + "\n"
        obj_str += "}" + "\n"
        try:
            self.mark_map_file_fd = open(self.mark_map_file_name, 'a')
            self.mark_map_file_fd.write(obj_str)
            self.mark_map_file_fd.flush()
            self.mark_map_file_fd.close()
            speed_limit = self.spinbox_cross_speed_limit.value()
            self.btnSetMarkMapSpeed(speed_limit, obj_str)
        except:
            pass
        
    ## set 
    def btnSetPlanAutoMode(self, btn, value):
        self.btn_plan_AutoMode.setStyleSheet("default")
        self.btn_plan_Human.setStyleSheet("default")
        btn.setStyleSheet("background-color: yellow")
        rospy.set_param("/autopilot/PilotMode", int(value))
        #if value == HumanMode:
        #    AutoPilotModeBtnClicked = HumanMode
        #    self.checkBox_auto_start_auto.setEnabled(False)
        #    self.checkBox_auto_start_auto.setChecked(False)
        #else:
        #    AutoPilotModeBtnClicked = AutoMode
        #    self.checkBox_auto_start_auto.setEnabled(True)

    ## set traffic light state
    def btnSetTraffficLightState(self, btn, value):
        self.btn_traffic_light_green.setStyleSheet("default")
        self.btn_traffic_light_red.setStyleSheet("default")
        self.btn_traffic_light_release.setStyleSheet("default")
        btn.setStyleSheet("background-color: yellow")
        rospy.set_param("/autopilot/TrafficLightCmd", int(value))

    ## set timer event
    def set_timer_event(self):
        ## common status msg
        self.timer1000hz = QtCore.QTimer(self)
        self.timer1000hz.timeout.connect(self.loop_1000hz)
        self.timer1000hz.start(1000)
        ## ros nodes status
        self.timer_10hz = QtCore.QTimer(self)
        self.timer_10hz.timeout.connect(self.loop_10hz)
        self.timer_10hz.start(10)

    ## 10 hz loop
    def loop_10hz(self):
        self.showGardianInfo()
        self.checkHumanMode_beta()
        self.checkAutoModeChange()
        
    ## 1000hz loop
    def loop_1000hz(self):
        self.text_browser_info = ""
        self.text_browser_info += self.getSettingInfo()
        self.text_browser_info += self.getCommonStateInfo()
        self.textBrowser_status.setText(self.text_browser_info)
        self.showMemStatus()
        self.showCpuStatus()
        #self.checkAutoStartAutoMode()
        self.showHzStatus()
        #self.checkBrakeToStopAuto()


    ## if checkBox_auto_start_auto
    def checkAutoStartAutoMode(self):
        global g_vstate_brake
        global g_vstate_throttle
        global g_vstate_brake_pre
        global g_vstate_throttle_pre
        if self.checkBox_auto_start_auto.isChecked() == True:
            if g_vstate_brake == 0 and g_vstate_throttle == 0:
                if g_vstate_brake_pre == 0 and g_vstate_throttle_pre == 0:
                    #rospy.set_param("/autopilot/PilotMode", AutoMode)
                    self.btn_plan_AutoMode.setStyleSheet("background-color: yellow")
                    self.btn_plan_Human.setStyleSheet("default")
        g_vstate_brake_pre    = g_vstate_brake
        g_vstate_throttle_pre = g_vstate_throttle
    
    def checkBrakeToStopAuto(self):
        global g_vstate_brake
        global g_vstate_throttle
        global g_vstate_brake_pre
        global g_vstate_throttle_pre
        global g_brake_secs
        if self.checkBox_brake_stop_auto.isChecked() == True:
            if g_vstate_brake != 0:
                if g_vstate_brake_pre != 0:
                    if g_brake_secs < 10:
                        g_brake_secs = g_brake_secs + 1
                    else:
                        #rospy.set_param("/autopilot/PilotMode", HumanMode)
                        self.btn_plan_AutoMode.setStyleSheet("default")
                        self.btn_plan_Human.setStyleSheet("background-color: yellow")
                        #self.checkBox_auto_start_auto.setEnabled(False)
                        self.checkBox_auto_start_auto.setChecked(False)
                        #AutoPilotModeBtnClicked = HumanMode
                        g_brake_secs = 0
                else:
                    g_brake_secs = 0
    

    ## if in auto mode,check if it turn to human drive,lock the log.
    def checkAutoModeChange(self):
        global Pre_mode
        cur_pilot_mode = rospy.get_param("/autopilot/PilotMode")
        if(cur_pilot_mode == AutoMode):
            pass
        elif (cur_pilot_mode == HumanMode):
            if (Pre_mode == AutoMode):
                ##
                self.btn_plan_AutoMode.setStyleSheet("default")
                ## lock log
                self.lock_log_pub.publish(0)
                Pre_mode = HumanMode
    
    #检测是否被接管
    def checkHumanMode(self):
        pilot_mode_ = rospy.get_param("/autopilot/PilotMode")
        #try:
        #    lon_mode_ = rospy.get_param("/autopilot/LongitudeDrvingMode")
        #except KeyError:
        #    lon_mode_ = -1
        global _count_
        if(pilot_mode_ == 1):
            # 0 是人工驾驶，非 0 是自动。
            if(g_longitude_driving_mode == 0):
                _count_ = _count_ + 1
            if (_count_ > 20):
                rospy.set_param("/autopilot/PilotMode", HumanMode)
                self.btn_plan_AutoMode.setStyleSheet("default")
                self.btn_plan_Human.setStyleSheet("background-color: yellow")
                _count_ = 0

    def checkHumanMode_beta(self):
        global g_pilot_mode
        global g_pilot_mode_pre
        if(g_pilot_mode == 0):
            if(g_pilot_mode_pre == 1):
                #_count_ = _count_ + 1
                rospy.set_param("/autopilot/PilotMode", HumanMode)
                self.btn_plan_AutoMode.setStyleSheet("default")
                self.btn_plan_Human.setStyleSheet("background-color: yellow")
        g_pilot_mode_pre = g_pilot_mode


    ## recv ros topic msg from topic /system/nodes
    def showGardianInfo(self):
        ### if the status string change format,maybe raise some exception.
        try:
            keys          = g_ros_gardian_msg_dict.keys()
            cur_item_cnt  = self.listWidget_ros_node.count()
            cur_item_dict = {}
            for i in range(cur_item_cnt):
                item = self.listWidget_ros_node.item(i)
                item_2 = self.listWidget_ros_node_2.item(i)

                text_list = item.text().split(":")
                cur_key = ""
                cur_val = ""
                if len(text_list) == 2:
                    cur_key = text_list[0]
                    cur_val = text_list[1]
                    cur_item_dict[cur_key] = cur_val

                if cur_key in g_ros_gardian_msg_dict.keys():
                    got_val = g_ros_gardian_msg_dict[cur_key]
                    if got_val == "on":
                        text = cur_key + ":" + "on"
                        item.setText(text)
                        item.setBackground(QColor('green'))

                        item_2.setText(text)
                        item_2.setBackground(QColor('green'))
                    elif got_val == "off":
                        text = cur_key + ":" + "off"
                        item.setText(text)
                        item.setBackground(QColor('red'))

                        item_2.setText(text)
                        item_2.setBackground(QColor('red'))
        except:
            pass

        ## add new node
        try:
            for key in keys:
                if key not in cur_item_dict.keys():
                    value = g_ros_gardian_msg_dict[key]
                    item  = QListWidgetItem()
                    item.setText(key + ":" + value)

                    item_2  = QListWidgetItem()
                    item_2.setText(key + ":" + value)
                    if value == "off":
                        item.setBackground(QColor('red'))
                        item_2.setBackground(QColor('red'))
                    else:
                        item.setBackground(QColor('green'))
                        item_2.setBackground(QColor('green'))
                    self.listWidget_ros_node.addItem(item)
                    self.listWidget_ros_node_2.addItem(item_2)
        except:
            pass

    ## get current setting info,to show it in monitor tab.
    def getSettingInfo(self):
        setting_info = "===== SETTINGS =====\n"
        setting_info += self.getParamAndCheck("/autopilot/PilotMode") + "  (1=Auto;0=Human)\n"
        setting_info += self.getParamAndCheck("/autopilot/VelocityMax") + " m/s(>0)\n"
        return setting_info

    ## get common stat info string
    def getCommonStateInfo(self):
        state_info = "===== STATE =====\n"
        state_info += self.getParamAndCheck("/autopilot/LaneChange") + " (0=keep;1=left;2=right)\n"
        state_info += self.getParamAndCheck("/autopilot/TrafficLightCmd") + " (0=release,1=red,2=green)\n"
        return state_info

    def getParamAndCheck(self, param_string):
        try:
            value = rospy.get_param(param_string)
        except KeyError:
            value = -1
        if isinstance(value, (float, str)):
            value = round(float(value), 2)
        res = param_string + "\t= " + str(value)
        return res

    def set_forPlan_enable(self, flag=False):
        self.btn_LaneChange_Left.setEnabled(flag)
        self.btn_LaneChange_KeepLane.setEnabled(flag)
        self.btn_LaneChange_Right.setEnabled(flag)
        self.spinbox_aimVelocity.setEnabled(flag)
        self.btn_plan_AutoMode.setEnabled(flag)
        self.btn_plan_Human.setEnabled(flag)
        self.btn_plan_SetVelocity.setEnabled(flag)
        #self.spinbox_aim_speed_mark_map.setEnabled(flag)
        self.spinbox_straight_speed_limit.setEnabled(flag)
        self.spinbox_left_speed_limit.setEnabled(flag)
        self.spinbox_right_speed_limit.setEnabled(flag)
        self.spinbox_cross_speed_limit.setEnabled(flag)
        self.checkBox_auto_start_auto.setEnabled(False)
        self.checkBox_brake_stop_auto.setEnabled(False)

    def resetLaneChangeBtn(self):
        self.btn_LaneChange_Left.setStyleSheet("default")
        self.btn_LaneChange_KeepLane.setStyleSheet("default")
        self.btn_LaneChange_Right.setStyleSheet("default")

    ## change lane
    def btnSetLaneChange(self, btn, val):
        self.resetLaneChangeBtn()
        btn.setStyleSheet("background-color: yellow")
        rospy.set_param("/autopilot/LaneChange", int(val))

    ## start to record track 
    def btnStartRecordTrack(self):
        ## check gnss
        if self.checkCanRecordTrack() == False:
            msg_info = "Can not get location data,so can not record track.Check localization node."
            QMessageBox.information(self,"OK", msg_info, QMessageBox.Yes )
            return False

        ## check if there is track_recorder
        if self.checkTrackRecorder() == False:
            return False

        self.btn_start_record_track.setStyleSheet("default")
        self.textBroswer_track_file.setText("start to record track")
        try:
            file_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
            self.record_track_log_file = self.record_track_file_path + "gui_ji_" + file_time + ".txt"
            self.textBroswer_track_file.setText(self.record_track_log_file)

            self.mark_map_file_name = self.mark_map_file_path + "da_dian_" + file_time + ".txt"
            self.textBroswer_mark_map_file.setText(self.mark_map_file_name)

            start_node_cmd = "rosrun track_recorder track_recorder _log_file:=" + self.record_track_log_file #+ " &"
            ## for not docker  
            # full_cmd = "gnome-terminal --tab -e \"bash -c " + "\'" + start_node_cmd + "\';bash\""
            # for docker
            full_cmd = "xfce4-terminal --tab -e \"bash -c " + "\'" + start_node_cmd + "\';bash\""
            full_cmd += " -T \"track-recorder\" &"  
            
            print("============ start track_recorder command ====================")
            print(full_cmd)
            print("==============================================================")
            os.system(full_cmd)
        except:
            self.textBroswer_track_file.setText("Start track_recorder got some error,try again.")
            return
    
    def checkCanRecordTrack(self):
        global MarkMapPosition_x
        global MarkMapPosition_y
        global MarkMapPosition_longitude
        global MarkMapPosition_latitude

        if MarkMapPosition_x != 0.0 or MarkMapPosition_longitude != 0:
            return True
        return False

    ## stop recording track
    def btnStopRecordTrack(self):
        self.btn_stop_record_track.setStyleSheet("default")
        self.textBroswer_track_file.setText("stop recording track...")
        stop_track_cmd = "rosnode kill track_recorder"
        os.system(stop_track_cmd) 
        self.textBroswer_track_file.setText("stoped! track file: " + self.record_track_log_file)
        print("============ stop track_recorder command =====================")
        print(stop_track_cmd)
        print("==============================================================")

    def btnExportTrackFile(self):
        ## check if there is traj_filter
        if self.checkTrajFilter() == False:
            return False

        ## export to new path
        track_file = self.record_track_log_file
        save_file_path = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    "Export To New Path", self.traj_file_path)
        diss_file = save_file_path[0]
        diss_file_mid = diss_file + "_disstance"
        if len(diss_file) == 0:
            return
        
        traj_filter_path  = self.traj_filter_exe_path 
        cmd_traj_disstance = traj_filter_path + \
                             "traj_filter distance "  + \
                             track_file + " " + diss_file_mid + " 0.2"
        os.system(cmd_traj_disstance)
        print("==== Export track record file, step 1, cmd ===================")
        print(cmd_traj_disstance)
        print("==============================================================")

        cmd_traj_kappa = traj_filter_path + \
                         "traj_filter kappa " + \
                         diss_file_mid + " " + diss_file + " 5"
        os.system(cmd_traj_kappa)
        print("==== Export track record file, step 2, cmd ===================")
        print(cmd_traj_kappa)
        print("==============================================================")
        msg_info = "Export track file to " + diss_file + " success."
        QMessageBox.information(self,"OK", msg_info, QMessageBox.Yes )

    ## lock ros log file
    def btnLockLog(self):
        click_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.lock_log_pub.publish(0)
        self.textBrowser_lock_log_status.setText(click_time)

    ### mem status
    def showMemStatus(self):
        self.mem_status_info = ""
        for key in g_ros_mem_msg_dict.keys():
            val = g_ros_mem_msg_dict[key]
            self.mem_status_info += key + " : " + val + "\n"
        self.textBrowser_mem_info.setText(self.mem_status_info)

    ## show cpu status
    def showCpuStatus(self):
        self.cpu_status_info = ""
        for key in g_ros_cpu_msg_dict.keys():
            val = g_ros_cpu_msg_dict[key]
            self.cpu_status_info += key + " : " + str(val) + "\n"
        self.textBrowser_cpu_info.setText(self.cpu_status_info)

    ## show hz status
    def showHzStatus(self):
        ### if the status string change format,maybe raise some exception.
        try:
            keys          = g_ros_hz_msg_dict.keys()
            cur_item_cnt  = self.listWidget_hz_status.count()
            cur_item_dict = {}
            for i in range(cur_item_cnt):
                item = self.listWidget_hz_status.item(i)
                text_list = item.text().split(":")
                cur_key = ""
                cur_val = ""
                if len(text_list) == 2:
                    cur_key = text_list[0]
                    cur_val = text_list[1]
                    cur_item_dict[cur_key] = cur_val

                if cur_key in g_ros_hz_msg_dict.keys():
                    got_val = g_ros_hz_msg_dict[cur_key]
                    text = cur_key + ":" + got_val
                    item.setText(text)
                    if float(got_val) > 0:
                        item.setBackground(QColor('green'))
        except:
            pass
        ## add new node
        try:
            for key in keys:
                if key not in cur_item_dict.keys():
                    value = g_ros_hz_msg_dict[key]
                    item  = QListWidgetItem()
                    item.setText(key + ":" + value)
                    if float(value) > 0:
                        item.setBackground(QColor('green'))
                    else:
                        item.setBackground(QColor('red'))
                    self.listWidget_hz_status.addItem(item)
        except:
            pass
        pass

    ### to store choose map file
    def btnSetChooseMapFilePath(self):
        self.set_choose_map_file_path = QtWidgets.QFileDialog.getSaveFileName(self,
                                            "Set Choose Map File", self.map_file_path)        
        self.set_choose_map_file = self.set_choose_map_file_path[0]
        if len(self.set_choose_map_file) == 0:
            return
        self.tbx_set_choose_map_file.setText(self.set_choose_map_file)

    ###
    def btnChooseTrajFile(self):
        self.choose_traj_file_path = ()
        self.choose_traj_file_path =  QtWidgets.QFileDialog.getOpenFileNames(self, 
                            "Choose Traj Files ", self.traj_file_path)
        self.choose_traj_files = self.choose_traj_file_path[0]
        self.all_traj_file_str = ""
        for name in self.choose_traj_files:
            self.all_traj_file_str += str(name) + ";"
        self.textBrowser_traj_file.setText(self.all_traj_file_str[:-1])

    def btnChooseMapFile(self):
        self.choose_map_file_path = QtWidgets.QFileDialog.getOpenFileName(self,
                                            "Choose Map File", self.mark_map_file_path)
        self.choose_map_file = self.choose_map_file_path[0]
        if len(self.choose_map_file) == 0:
            return
        self.textBrowser_map_file.setText(self.choose_map_file)    
        
    ### 
    def btnAddMap(self):
        try:
            traj_file = self.choose_traj_files[-1]
            f = open(traj_file)
            lines = f.readlines()
            end_line = lines[-1]
            x_y = end_line.split(",")
            end_x = x_y[0]
            end_y = x_y[1]
            f.close()

            traj_file_str = self.textBrowser_traj_file.document().toPlainText()
            map_file_str  = self.textBrowser_map_file.document().toPlainText()
            point_list = []
            point_dict = {}
            point_dict["name"] = self.textBrowser_end_point_name.document().toPlainText()
            point_dict["x"]    = str(end_x)
            point_dict["y"]    = str(end_y)
            point_list.append(point_dict)
            map_dict = {}
            map_dict["name"]        = self.textBrowser_map_name.document().toPlainText()
            map_dict["traj"]        = traj_file_str
            map_dict["feature_map"] = map_file_str
            map_dict["points"]      = point_list
            map_list = []
            map_list.append(map_dict) 
            choose_map_file = self.tbx_set_choose_map_file.document().toPlainText()
            print("choose_map_file: " + choose_map_file)

            #if len(choose_map_file) == 0:
            #    file_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            #    choose_map_file = self.home_path + "/choose_map_" + file_time + ".json"
            if len(choose_map_file) == 0:
                QMessageBox.information(self,"Error","Please set map file path.")
                return

            self.tbx_set_choose_map_file.setText(choose_map_file)
            
            ff_data = ""
            if os.path.exists(choose_map_file):
                ff = open(choose_map_file, "r+")
                ff_data = ff.read()
                ff.close()

            if len(str(ff_data)) > 0:
                self.map_total = json.loads(str(ff_data))
                ## remove old map have same name with new added map
                map_total_cnt = len(self.map_total["map"])
                for i in range(map_total_cnt - 1, -1, -1):
                    if self.map_total["map"][i]["name"] == map_dict["name"]:
                        self.map_total["map"].remove(self.map_total["map"][i])
                      
                if len(self.map_total.keys()) == 0:
                    self.map_total["map"] = map_list
                else:        
                    self.map_total["map"].append(map_dict)              
            else:
                self.map_total["map"] = map_list
            map_json_str = json.dumps(self.map_total)

            ff = open(choose_map_file, "w")
            ff.write(map_json_str)
            ff.close()
            print("============= Generate choose_map.json content ===============")
            print("file path: " + choose_map_file)
            print(map_json_str)
            print("==============================================================")
        except:
            QMessageBox.information(self,"Error","Generate choose map file fail.")

    ## set a new file for mark map,and init the counters.
    def btnSetNewMarkMapFile(self):
        self.stop_cross_walk = 0
        self.stop_line = 0
        self.speed_limit_num = 0
        file_time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        self.mark_map_file_name = self.mark_map_file_path + "da_dian_" + file_time + ".txt"
        self.textBroswer_mark_map_file.setText(self.mark_map_file_name)
        
    def btnLoadTrackFile(self):
        self.load_track_file_path = QtWidgets.QFileDialog.getOpenFileName(self,
                                            "Load Track File", self.record_track_file_path)
        self.record_track_log_file = self.load_track_file_path[0]
        if len(self.record_track_log_file) == 0:
            return
        self.textBroswer_track_file.setText(self.record_track_log_file) 

def quit(signum, frame):
    print('Closing the chassis_control GUI!')
    sys.exit()

if __name__ == "__main__":
    app = Application(sys.argv)
    window = MyApp()
    window.show()
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    sys.exit(app.exec_())
