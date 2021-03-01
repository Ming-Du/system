#!/bin/bash
rosnode kill -a
ps aux | grep roscore |awk '{print $2}' |xargs kill

sudo chmod +777 /dev -R
source ~/catkin_ws/devel/setup.bash
echo $HOME

###########################################################
GLOG_COMMAND="export GLOG_logtostderr=1; export GLOG_colorlogtostderr=1"

# sudo arp -i eno1 -s 192.168.0.3 00:0c:29:80:00:01
ROSCORE="roscore"
GNSS_COMMAND="roslaunch drivers_gnss data_spin.launch "
LOCALIZATION="roslaunch launch path_recorder.launch"
CANCARD="bash ~/EMUC_B202/start.sh"
CANBUS="roslaunch launch chassis.launch"
BYD_CAN_ADAPTER="roslaunch byd_can_adapter byd_can_adapter.launch"
JINLV_CAN_ADAPTER="roslaunch can_adapter jinlv_can_adapter.launch"
RTKREPLAYPLANNER="roslaunch controller_simulator controller_simulator.launch"
SIM_VEHICLEDYNAMICANDMAP="roslaunch controller_simulator simulator_vehicledynamicandmap.launch"
CONTROLLER="roslaunch controller controller.launch"
SEND_CONTROL_COMMAND="python2 share/cmd_panel/chassis_set.py qt5"
SEND_CONTROL_COMMAND_USE_TOPIC="python2 src/control/chassis_tool/chassis_set_pbmsg.py"
VEHICLE_MODEL="rosrun controller_simulator vehicle_dynamics"
# PERCEPTION="roslaunch src/control/script/telematics_for_auto.launch"
PERCEPTION="roslaunch launch perception.launch"
#PERCEPTION_BYD="roslaunch launchperception_BYDADK2721.launch"
CHEJI="roslaunch telematics telematics.launch"
LOCAL_PLANNER="roslaunch launch local_planning.launch"
SIM_LOCAL_PLANNER="roslaunch launch sim_local_planning.launch"
HAD_MAP="roslaunch launch hadmap.launch"
SIM_HAD_MAP="roslaunch launch sim_hadmap.launch"
TRAFFIC_LIGHT="roslaunch traffic_light traffic_light.launch"
GLOBALLOC2LOCAL="rosrun controller_simulator globalloc2local"
LIDAR_CAMERA_DRIVERS="roslaunch launch drivers.launch"
TRAFFIC_LANE="roslaunch src/perception/lane_detection/lane_detection_cpp/launch/lane_detection_cpp.launch"
#OPERATOR_TOOL="python2 src/tools/operator_tool/operator_tool.py qt5 src/tools/operator_tool/conf.txt"
OPERATOR_TOOL="roslaunch operator_tool operator_tool.launch"
GUARDIAN="roslaunch guardian system_guardian.launch"

# change the    omstreambuf() : buf  (4096*10)   
##for the min auto drive mode ,just use RTK_PLANNER and controller
if [ "$1" == "1" ]; then
gnome-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GNSS_COMMAND';bash" -t "gnss_rtk"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CANBUS';bash" -t "canbus"  \
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
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CANBUS';bash" -t "canbus"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -t "drivers"  \
	    --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -t "perception" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -t "cheji" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -t "local_planner" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -t "had_map" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRAFFIC_LIGHT';bash" -t "traffic_light" \
		--tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -t "operator_tool" \
        --tab -e "bash -c 'sleep 2';bash";
#for perception mode only lane_detection 
elif [ "$1" == "3" ]; then
gnome-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CANBUS';bash" -t "canbus"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -t "drivers"  \
	    --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CHEJI';bash" -t "cheji" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -t "local_planner" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRAFFIC_LANE';bash" -t "traffic_lane" \
		--tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -t "operator_tool" \
        --tab -e "bash -c 'sleep 2';bash";
##for offline simulator,use had_map build map
elif [ "$1" == "4" ]; then
gnome-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $SIM_VEHICLEDYNAMICANDMAP';bash" -t "planner"  \
	    --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
	--tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GLOBALLOC2LOCAL';bash" -t "globalloc2local"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $SIM_LOCAL_PLANNER';bash" -t "local_planner" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $SIM_HAD_MAP';bash" -t "had_map" \
        --tab -e "bash -c 'sleep 2';bash";$SEND_CONTROL_COMMAND_USE_TOPIC
##for offline simulator,use traffic_lane build map  ,rtk_planner is a reference map (shutdown the traj_pub)
elif [ "$1" == "5" ]; then
gnome-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $RTKREPLAYPLANNER';bash" -t "rtk_planner"  \
	    --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
	--tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GLOBALLOC2LOCAL';bash" -t "globalloc2local"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -t "local_planner" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $TRAFFIC_LANE';bash" -t "lane_detection" \
		--tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $OPERATOR_TOOL';bash" -t "operator_tool" \
        --tab -e "bash -c 'sleep 2';bash";
#min autodrive system 
elif [ "$1" == "0" ]; then
    gnome-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GNSS_COMMAND';bash" -t "gnss_rtk"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $BYD_CAN_ADAPTER';bash" -t "canbus"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $RTKREPLAYPLANNER';bash" -t "planner"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
        --tab -e "bash -c 'sleep 2';bash";$SEND_CONTROL_COMMAND_USE_TOPIC
elif [ "$1" == "6" ]; then
    gnome-terminal	--window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LIDAR_CAMERA_DRIVERS';bash" -t "gnss_rtk"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $JINLV_CAN_ADAPTER';bash" -t "canadapter"  \
        --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $PERCEPTION';bash" -t "perception"  \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -t "local_planner" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $HAD_MAP';bash" -t "had_map" \
        --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CONTROLLER';bash" -t "controller"  \
        --tab -e "bash -c 'sleep 2';bash";$SEND_CONTROL_COMMAND_USE_TOPIC
elif [ "$1" == "wey" ]; then
    gnome-terminal  --window -e "bash -c '$GLOG_COMMAND && $ROSCORE';bash" -t "core" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $LOCALIZATION';bash" -t "localization" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $CANBUS';bash" -t "canbus"  \
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
      --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $CANCARD';bash" -t "cancard" \
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $JINLV_CAN_ADAPTER';bash" -t "canbus"  \
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
      --tab -e "bash -c 'sleep 3; $GLOG_COMMAND && $BYD_CAN_ADAPTER';bash" -t "canbus"  \
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
     
# --tab -e "bash -c 'sleep 1; $GLOG_COMMAND && $RTKREPLAYPLANNER';bash" -t "planner"  \
        # --tab -e "bash -c 'sleep 1; $GLOG_COMMAND && $CANCARD';bash" -t "cancard"  \
	# --tab -e "python -c 'sleep 1; $GLOG_COMMAND && $SEND_CONTROL_COMMAND';python" -t "send_command""
	# --tab -e "python python2 src/control/chassis_tool/chassis_set.py qt5"
    # --window -e \
# if [ $2 -eq 1 -o  $2 = "rtk_planner" ]; then
#     echo "rtk_planner"
# elif [ $2 -eq 2 -o $2 = "local_planner" ]; then
#     echo "local_planner"
#     --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $LOCAL_PLANNER';bash" -t "local_planner" 
# else
#     echo "do_other"
# fi
        # --tab -e "bash -c 'sleep 2; $GLOG_COMMAND && $GNSS_COMMAND';bash" -t "gnss_rtk"  \
       
