#!/bin/bash
rosnode kill -a
ps aux | grep roscore |awk '{print $2}' |xargs kill

sudo chmod +777 /dev -R
echo $HOME
echo $1
###########################################################
GLOG_COMMAND="export GLOG_logtostderr=1; export GLOG_colorlogtostderr=1"

ROSCORE="roscore"
GNSS_COMMAND="roslaunch drivers_gnss data_spin.launch "
#LOCALIZATION="roslaunch launch path_recorder.launch"
LOCALIZATION="roslaunch localization localization.launch"
VV6_CAN_ADAPTER="roslaunch can_adapter vv6_can_adapter.launch"
BYD_CAN_ADAPTER="roslaunch byd_can_adapter byd_can_adapter.launch"
JINLV_CAN_ADAPTER="roslaunch can_adapter jinlv_can_adapter.launch"
RTKREPLAYPLANNER="roslaunch controller_simulator controller_simulator.launch"
CONTROLLER="roslaunch controller controller.launch"
SEND_CONTROL_COMMAND="python2 share/cmd_panel/chassis_set.py qt5"
SEND_CONTROL_COMMAND_USE_TOPIC="python2 src/control/chassis_tool/chassis_set_pbmsg.py"
PERCEPTION="roslaunch launch perception.launch"
CHEJI="roslaunch telematics telematics.launch"
LOCAL_PLANNER="roslaunch launch local_planning.launch"
HAD_MAP="roslaunch launch hadmap.launch"
TRAFFIC_LIGHT="roslaunch traffic_light traffic_light.launch"
LIDAR_CAMERA_DRIVERS="roslaunch launch drivers.launch"
TRAFFIC_LANE="roslaunch src/perception/lane_detection/lane_detection_cpp/launch/lane_detection_cpp.launch"
OPERATOR_TOOL="roslaunch operator_tool operator_tool.launch"
GUARDIAN="roslaunch guardian system_guardian.launch"
TRACK_RECORDER="roslaunch track_recorder track_recorder.launch"

##for the min auto drive mode ,just use RTK_PLANNER and controller
if [ "$1" == "1" ]; then
gnome-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GNSS_COMMAND';bash" -t "gnss_rtk"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $VV6_CAN_ADAPTER';bash" -t "canadapter"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $RTKREPLAYPLANNER';bash" -t "planner"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -t "perception" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -t "cheji" \
		--tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -t "operator_tool" \
        --tab -e "bash -c 'sleep 2';bash";
##for perception mode  tracffic light and lidar dectection
elif [ "$1" == "2" ]; then
gnome-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $VV6_CAN_ADAPTER';bash" -t "canadapter"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -t "drivers"  \
	    --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -t "perception" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -t "cheji" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -t "local_planner" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -t "had_map" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRAFFIC_LIGHT';bash" -t "traffic_light" \
		--tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -t "operator_tool" \
        --tab -e "bash -c 'sleep 2';bash";
elif [ "$1" == "wey" ]; then
    gnome-terminal  --window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $VV6_CAN_ADAPTER';bash" -t "canadapter"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -t "drivers"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -t "perception" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -t "cheji" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -t "local_planner" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -t "had_map" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRAFFIC_LIGHT';bash" -t "traffic_light" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GUARDIAN';bash" -t "guardian" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -t "operator_tool" \
      --tab -e "bash -c 'sleep 2';bash";
elif [ "$1" == "jinlv" ]; then
    gnome-terminal  --window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $JINLV_CAN_ADAPTER';bash" -t "canadapter"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -t "drivers"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -t "perception" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -t "cheji" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -t "local_planner" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -t "had_map" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRAFFIC_LIGHT';bash" -t "traffic_light" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GUARDIAN';bash" -t "guardian" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -t "operator_tool" \
      --tab -e "bash -c 'sleep 2';bash";
elif [ "$1" == "byd" ]; then
    gnome-terminal  --window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $BYD_CAN_ADAPTER';bash" -t "canadapter"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -t "drivers"  \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -t "perception" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -t "cheji" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -t "local_planner" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -t "had_map" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRAFFIC_LIGHT';bash" -t "traffic_light" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GUARDIAN';bash" -t "guardian" \
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -t "operator_tool" \
      --tab -e "bash -c 'sleep 2';bash";
else
    echo "do others"
fi

