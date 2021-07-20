#!/bin/bash
rosnode kill -a
ps aux | grep roscore |awk '{print $2}' |xargs kill

export DATE=`date +"%Y%m%d"`
export TIME=`date +"%H%M%S"`

sudo chmod +777 /dev -R
echo $HOME
echo $1
###########################################################
export GLOG_logtostderr=1; 
export GLOG_colorlogtostderr=1; 
export ROS_LOG_DIR=/home/mogo/data/log/${DATE}_${TIME}

[[ ! -d $ROS_LOG_DIR ]] && mkdir -p $ROS_LOG_DIR

source /home/mogo/autopilot/share/launch/bashrc.sh

GLOG_COMMAND="export GLOG_logtostderr=1; export GLOG_colorlogtostderr=1; export ROS_LOG_DIR=/home/mogo/data/log/${DATE}_${TIME}"
BASHRC="/home/mogo/autopilot/share/launch/bashrc.sh"
ROSCORE="source $BASHRC && roscore 2>&1 | tee \${ROS_LOG_DIR}/roscore.log"
GNSS_COMMAND="source $BASHRC && roslaunch drivers_gnss data_spin.launch 2>&1 | tee ${ROS_LOG_DIR}/data_spin.launch.log"
#LOCALIZATION="source $BASHRC roslaunch launch path_recorder.launch 2>&1 | tee \${ROS_LOG_DIR}/.log"
LOCALIZATION="source $BASHRC && roslaunch localization localization.launch 2>&1 | tee ${ROS_LOG_DIR}/localization.launch.log"
VV6_CAN_ADAPTER="source $BASHRC && roslaunch can_adapter vv6_can_adapter.launch 2>&1 | tee ${ROS_LOG_DIR}/vv6_can_adapter.launch.log"
BYD_CAN_ADAPTER="source $BASHRC && roslaunch can_adapter byd_can_adapter.launch 2>&1 | tee ${ROS_LOG_DIR}/byd_can_adapter.launch.log"
JINLV_CAN_ADAPTER="source $BASHRC && roslaunch can_adapter jinlv_can_adapter.launch 2>&1 | tee ${ROS_LOG_DIR}/jinlv_can_adapter.launch.log"
RTKREPLAYPLANNER="source $BASHRC && roslaunch controller_simulator controller_simulator.launch 2>&1 | tee ${ROS_LOG_DIR}/controller_simulator.launch.log"
CONTROLLER="source $BASHRC && roslaunch controller controller.launch 2>&1 | tee ${ROS_LOG_DIR}/controller.launch.log"
SEND_CONTROL_COMMAND="source $BASHRC && python2 share/cmd_panel/chassis_set.py qt5 2>&1 | tee \${ROS_LOG_DIR}/chassis_set.py.log"
SEND_CONTROL_COMMAND_USE_TOPIC="source $BASHRC && python2 src/control/chassis_tool/chassis_set_pbmsg.py 2>&1 | tee \${ROS_LOG_DIR}/chassis_set_pbmsg.py.log"
PERCEPTION="source $BASHRC && roslaunch launch perception.launch 2>&1 | tee ${ROS_LOG_DIR}/perception.launch.log"
CHEJI="source $BASHRC && roslaunch telematics telematics.launch 2>&1 | tee ${ROS_LOG_DIR}/telematics.launch.log"
LOCAL_PLANNER="source $BASHRC && roslaunch launch local_planning.launch 2>&1 | tee ${ROS_LOG_DIR}/local_planning.launch.log"
HAD_MAP="source $BASHRC && roslaunch launch hadmap.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap.launch.log"
TRAFFIC_LIGHT="source $BASHRC && roslaunch trt_yolov5 obj_6mm.launch 2>&1 | tee \${ROS_LOG_DIR}/trt_yolov5 obj_6mm.launch.log"
LIDAR_CAMERA_DRIVERS="source $BASHRC && roslaunch launch drivers.launch 2>&1 | tee ${ROS_LOG_DIR}/drivers.launch.log"
TRAFFIC_LANE="source $BASHRC && roslaunch src/perception/lane_detection/lane_detection_cpp/launch/lane_detection_cpp.launch 2>&1 | tee \${ROS_LOG_DIR}/lane_detection_cpp.launch.log"
OPERATOR_TOOL="source $BASHRC && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log"
GUARDIAN="source $BASHRC && roslaunch guardian system_guardian.launch 2>&1 | tee ${ROS_LOG_DIR}/system_guardian.launch.log"
TRACK_RECORDER="source $BASHRC && roslaunch track_recorder track_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/track_recorder.launch.log"
ROSBAG_RECORD="source $BASHRC && roslaunch rosbag_recorder rosbag_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/rosbag_recorder.launch.log"

##for the min auto drive mode ,just use RTK_PLANNER and controller
if [ "$1" == "1" ]; then
    roscore 2>&1 | tee ${ROS_LOG_DIR}/roscore.log &
    sleep 2 && roslaunch drivers_gnss data_spin.launch 2>&1 | tee ${ROS_LOG_DIR}/data_spin.launch.log &
    sleep 3 && roslaunch localization localization.launch 2>&1 | tee ${ROS_LOG_DIR}/localization.launch.log &
    sleep 3 && roslaunch can_adapter vv6_can_adapter.launch 2>&1 | tee ${ROS_LOG_DIR}/vv6_can_adapter.launch.log &
    sleep 2 && roslaunch controller_simulator controller_simulator.launch 2>&1 | tee ${ROS_LOG_DIR}/controller_simulator.launch.log &
    sleep 2 && roslaunch controller controller.launch 2>&1 | tee ${ROS_LOG_DIR}/controller.launch.log &
    sleep 3 && roslaunch launch perception.launch 2>&1 | tee ${ROS_LOG_DIR}/perception.launch.log &
    sleep 15 && roslaunch telematics telematics.launch 2>&1 | tee ${ROS_LOG_DIR}/telematics.launch.log &
	  sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
    sleep 3 && roslaunch hadmap_engine hadmap_engine.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap_engine.launch.log &
    sleep 2
##for perception mode  tracffic light and lidar dectection
elif [ "$1" == "2" ]; then
    roscore 2>&1 | tee ${ROS_LOG_DIR}/roscore.log &
    sleep 3 && roslaunch localization localization.launch 2>&1 | tee ${ROS_LOG_DIR}/localization.launch.log &
    sleep 3 && roslaunch can_adapter vv6_can_adapter.launch 2>&1 | tee ${ROS_LOG_DIR}/vv6_can_adapter.launch.log &
    sleep 2 && roslaunch launch drivers.launch 2>&1 | tee ${ROS_LOG_DIR}/drivers.launch.log &
	  sleep 2 && roslaunch controller controller.launch 2>&1 | tee ${ROS_LOG_DIR}/controller.launch.log &
    sleep 3 && roslaunch launch perception.launch 2>&1 | tee ${ROS_LOG_DIR}/perception.launch.log &
    sleep 15 && roslaunch telematics telematics.launch 2>&1 | tee ${ROS_LOG_DIR}/telematics.launch.log &
    sleep 2 && roslaunch launch local_planning.launch 2>&1 | tee ${ROS_LOG_DIR}/local_planning.launch.log &
    sleep 2 && roslaunch launch hadmap.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap.launch.log &
	  sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
    sleep 3 && roslaunch hadmap_engine hadmap_engine.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap_engine.launch.log &
    sleep 2
elif [ "$1" == "wey" ]; then
  roscore 2>&1 | tee ${ROS_LOG_DIR}/roscore.log &
  sleep 2 && roslaunch guardian system_guardian.launch 2>&1 | tee ${ROS_LOG_DIR}/system_guardian.launch.log &
  sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
  sleep 3 && roslaunch localization localization.launch 2>&1 | tee ${ROS_LOG_DIR}/localization.launch.log &
  sleep 3 && roslaunch can_adapter vv6_can_adapter.launch 2>&1 | tee ${ROS_LOG_DIR}/vv6_can_adapter.launch.log &
  sleep 2 && roslaunch launch drivers.launch 2>&1 | tee ${ROS_LOG_DIR}/drivers.launch.log &
  sleep 2 && roslaunch controller controller.launch 2>&1 | tee ${ROS_LOG_DIR}/controller.launch.log &
  sleep 3 && roslaunch launch perception.launch 2>&1 | tee ${ROS_LOG_DIR}/perception.launch.log &
  sleep 15 && roslaunch telematics telematics.launch 2>&1 | tee ${ROS_LOG_DIR}/telematics.launch.log &
  sleep 2 && roslaunch launch local_planning.launch 2>&1 | tee ${ROS_LOG_DIR}/local_planning.launch.log &
  sleep 2 && roslaunch launch hadmap.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap.launch.log &
  sleep 2 && roslaunch track_recorder track_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/track_recorder.launch.log &
  sleep 4 && roslaunch rosbag_recorder rosbag_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/rosbag_recorder.launch.log &
  sleep 3 && roslaunch hadmap_engine hadmap_engine.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap_engine.launch.log &
  sleep 2
elif [ "$1" == "df" ]; then
  roscore 2>&1 | tee ${ROS_LOG_DIR}/roscore.log &
  sleep 2 && source $BASHRC && roslaunch --wait guardian system_guardian.launch 2>&1 | tee ${ROS_LOG_DIR}/system_guardian.launch.log &
  sleep 2 && source $BASHRC && roslaunch --wait operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
  sleep 5 && source $BASHRC && roslaunch --wait localization localization.launch 2>&1 | tee ${ROS_LOG_DIR}/localization.launch.log &
  sleep 3 && source $BASHRC && roslaunch --wait can_adapter vv6_can_adapter.launch 2>&1 | tee ${ROS_LOG_DIR}/vv6_can_adapter.launch.log &
  sleep 3 && source $BASHRC && roslaunch --wait launch drivers.launch 2>&1 | tee ${ROS_LOG_DIR}/drivers.launch.log &
  sleep 2 && source $BASHRC && roslaunch --wait controller controller.launch 2>&1 | tee ${ROS_LOG_DIR}/controller.launch.log &
  sleep 7 && source $BASHRC && roslaunch --wait launch perception.launch 2>&1 | tee ${ROS_LOG_DIR}/perception.launch.log &
  sleep 15 && source $BASHRC && roslaunch --wait telematics telematics.launch 2>&1 | tee ${ROS_LOG_DIR}/telematics.launch.log &
  sleep 2 && source $BASHRC && roslaunch --wait launch local_planning.launch 2>&1 | tee ${ROS_LOG_DIR}/local_planning.launch.log &
  sleep 2 && source $BASHRC && roslaunch --wait launch hadmap.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap.launch.log &
  sleep 2 && source $BASHRC && roslaunch --wait track_recorder track_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/track_recorder.launch.log &
  sleep 17 && source $BASHRC && roslaunch --wait rosbag_recorder rosbag_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/rosbag_recorder.launch.log &
  sleep 3 && source $BASHRC && roslaunch --wait hadmap_engine hadmap_engine.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap_engine.launch.log &
  sleep 2
elif [ "$1" == "jinlv" ]; then
  roscore 2>&1 | tee ${ROS_LOG_DIR}/roscore.log &
  sleep 2 && roslaunch guardian system_guardian.launch 2>&1 | tee ${ROS_LOG_DIR}/system_guardian.launch.log &
  sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
  sleep 3 && roslaunch localization localization.launch 2>&1 | tee ${ROS_LOG_DIR}/localization.launch.log &
  sleep 3 && roslaunch can_adapter jinlv_can_adapter.launch 2>&1 | tee ${ROS_LOG_DIR}/jinlv_can_adapter.launch.log &
  sleep 2 && roslaunch launch drivers.launch 2>&1 | tee ${ROS_LOG_DIR}/drivers.launch.log &
  sleep 2 && roslaunch controller controller.launch 2>&1 | tee ${ROS_LOG_DIR}/controller.launch.log &
  sleep 3 && roslaunch launch perception.launch 2>&1 | tee ${ROS_LOG_DIR}/perception.launch.log &
  sleep 15 && roslaunch telematics telematics.launch 2>&1 | tee ${ROS_LOG_DIR}/telematics.launch.log &
  sleep 2 && roslaunch launch local_planning.launch 2>&1 | tee ${ROS_LOG_DIR}/local_planning.launch.log &
  sleep 2 && roslaunch launch hadmap.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap.launch.log &
  sleep 2 && roslaunch track_recorder track_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/track_recorder.launch.log &
  sleep 4 && roslaunch rosbag_recorder rosbag_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/rosbag_recorder.launch.log &
  sleep 3 && roslaunch hadmap_engine hadmap_engine.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap_engine.launch.log &
  sleep 2
elif [ "$1" == "byd" ]; then
  roscore 2>&1 | tee ${ROS_LOG_DIR}/roscore.log &
  sleep 2 && roslaunch guardian system_guardian.launch 2>&1 | tee ${ROS_LOG_DIR}/system_guardian.launch.log &
  sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
  sleep 3 && roslaunch localization localization.launch 2>&1 | tee ${ROS_LOG_DIR}/localization.launch.log &
  sleep 3 && roslaunch can_adapter byd_can_adapter.launch 2>&1 | tee ${ROS_LOG_DIR}/byd_can_adapter.launch.log &
  sleep 2 && roslaunch launch drivers.launch 2>&1 | tee ${ROS_LOG_DIR}/drivers.launch.log &
  sleep 2 && roslaunch controller controller.launch 2>&1 | tee ${ROS_LOG_DIR}/controller.launch.log &
  sleep 3 && roslaunch launch perception.launch 2>&1 | tee ${ROS_LOG_DIR}/perception.launch.log &
  sleep 15 && roslaunch telematics telematics.launch 2>&1 | tee ${ROS_LOG_DIR}/telematics.launch.log &
  sleep 2 && roslaunch launch local_planning.launch 2>&1 | tee ${ROS_LOG_DIR}/local_planning.launch.log &
  sleep 2 && roslaunch launch hadmap.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap.launch.log &
  sleep 2 && roslaunch track_recorder track_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/track_recorder.launch.log &
  sleep 4 && roslaunch rosbag_recorder rosbag_recorder.launch 2>&1 | tee ${ROS_LOG_DIR}/rosbag_recorder.launch.log &
  sleep 3 && roslaunch hadmap_engine hadmap_engine.launch 2>&1 | tee ${ROS_LOG_DIR}/hadmap_engine.launch.log &
  sleep 2
else
    echo "do others"
fi

