#!/bin/bash
rosnode kill -a
ps aux | grep roscore |awk '{print $2}' |xargs kill

sudo chmod +777 /dev -R
echo $HOME
echo $1
###########################################################
GLOG_COMMAND="export GLOG_logtostderr=1; export GLOG_colorlogtostderr=1"
BASHRC="/home/mogo/autopilot/share/launch/bashrc.sh"
ROSCORE="source $BASHRC && roscore"
GNSS_COMMAND="source $BASHRC && roslaunch drivers_gnss data_spin.launch "
#LOCALIZATION="source $BASHRC roslaunch launch path_recorder.launch"
LOCALIZATION="source $BASHRC && roslaunch localization localization.launch"
VV6_CAN_ADAPTER="source $BASHRC && roslaunch can_adapter vv6_can_adapter.launch"
BYD_CAN_ADAPTER="source $BASHRC && roslaunch can_adapter byd_can_adapter.launch"
JINLV_CAN_ADAPTER="source $BASHRC && roslaunch can_adapter jinlv_can_adapter.launch"
RTKREPLAYPLANNER="source $BASHRC && roslaunch controller_simulator controller_simulator.launch"
CONTROLLER="source $BASHRC && roslaunch controller controller.launch"
SEND_CONTROL_COMMAND="source $BASHRC && python2 share/cmd_panel/chassis_set.py qt5"
SEND_CONTROL_COMMAND_USE_TOPIC="source $BASHRC && python2 src/control/chassis_tool/chassis_set_pbmsg.py"
PERCEPTION="source $BASHRC && roslaunch launch perception.launch"
CHEJI="source $BASHRC && roslaunch telematics telematics.launch"
LOCAL_PLANNER="source $BASHRC && roslaunch launch local_planning.launch"
HAD_MAP="source $BASHRC && roslaunch launch hadmap.launch"
TRAFFIC_LIGHT="source $BASHRC && roslaunch trt_yolov5 obj_6mm.launch"
LIDAR_CAMERA_DRIVERS="source $BASHRC && roslaunch launch drivers.launch"
TRAFFIC_LANE="source $BASHRC && roslaunch src/perception/lane_detection/lane_detection_cpp/launch/lane_detection_cpp.launch"
OPERATOR_TOOL="source $BASHRC && roslaunch operator_tool operator_tool.launch"
GUARDIAN="source $BASHRC && roslaunch guardian system_guardian.launch"
TRACK_RECORDER="source $BASHRC && roslaunch track_recorder track_recorder.launch"
ROSBAG_RECORD="source $BASHRC && roslaunch rosbag_recorder rosbag_recorder.launch"

##for the min auto drive mode ,just use RTK_PLANNER and controller
if [ "$1" == "1" ]; then
xfce4-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -T "core" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GNSS_COMMAND';bash" -T "gnss_rtk"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -T "localization" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $VV6_CAN_ADAPTER';bash" -T "canadapter"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $RTKREPLAYPLANNER';bash" -T "planner"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -T "controller"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -T "perception" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -T "cheji" \
		--tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -T "operator_tool" \
        --tab -e "bash -c 'sleep 2';bash";
##for perception mode  tracffic light and lidar dectection
elif [ "$1" == "2" ]; then
xfce4-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -T "core" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -T "localization" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $VV6_CAN_ADAPTER';bash" -T "canadapter"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -T "drivers"  \
	    --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -T "controller"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -T "perception" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -T "cheji" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -T "local_planner" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -T "had_map" \
		--tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -T "operator_tool" \
        --tab -e "bash -c 'sleep 2';bash";
elif [ "$1" == "wey" ]; then
    xfce4-terminal  --window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -T "core" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -T "localization" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $VV6_CAN_ADAPTER';bash" -T "canadapter"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -T "drivers"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -T "controller"  \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -T "perception" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -T "cheji" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -T "local_planner" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -T "had_map" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GUARDIAN';bash" -T "guardian" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -T "operator_tool" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRACK_RECORDER';bash" -T "track_recorder" \
      --tab -e "bash -c 'sleep 4; $GLOG_COMMAND && $ROSBAG_RECORD';bash" -T "rosbag_recorder" \
      --tab -e "bash -c 'sleep 2';bash";
elif [ "$1" == "jinlv" ]; then
    xfce4-terminal  --window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -T "core" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -T "localization" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $JINLV_CAN_ADAPTER';bash" -T "canadapter"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -T "drivers"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -T "controller"  \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -T "perception" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -T "cheji" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -T "local_planner" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -T "had_map" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GUARDIAN';bash" -T "guardian" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -T "operator_tool" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRACK_RECORDER';bash" -T "track_recorder" \
      --tab -e "bash -c 'sleep 4; $GLOG_COMMAND && $ROSBAG_RECORD';bash" -T "rosbag_recorder" \
      --tab -e "bash -c 'sleep 2';bash";
elif [ "$1" == "byd" ]; then
    xfce4-terminal  --window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -T "core" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -T "localization" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $BYD_CAN_ADAPTER';bash" -T "canadapter"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -T "drivers"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -T "controller"  \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -T "perception" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -T "cheji" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -T "local_planner" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -T "had_map" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GUARDIAN';bash" -T "guardian" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -T "operator_tool" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRACK_RECORDER';bash" -T "track_recorder" \
      --tab -e "bash -c 'sleep 4; $GLOG_COMMAND && $ROSBAG_RECORD';bash" -T "rosbag_recorder" \
      --tab -e "bash -c 'sleep 2';bash";
else
    echo "do others"
fi

