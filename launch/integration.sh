#!/bin/bash

start_node_terminal(){
    # echo "func::VehicleType:$VehicleType"  #wey|byd|jinlv|df
    # echo "func::GuiServer:$GuiServer"  #background|xfce4|gnome
    # echo "func::RunMode:$RunMode"  #normal|debug
    # echo "func::LOG_ENV:$LOG_ENV"
    # echo "func::BASHRC:$BASHRC"
    echo "func::GuiTerminal:$GuiTerminal"
    echo "func::TitleOpt:$TitleOpt"
    # return
    if [ "$VehicleType" == "wey" ];then
        $GuiTerminal  --window -e "bash -c '$LOG_ENV && $BASHRC && $ROSCORE';bash" $TitleOpt "core" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $LOCALIZATION';bash" $TitleOpt "localization" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $VV6_CAN_ADAPTER';bash" $TitleOpt "canadapter"  \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LIDAR_CAMERA_DRIVERS';bash" $TitleOpt "drivers"  \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $VV6_CONTROLLER';bash" $TitleOpt "controller"  \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $PERCEPTION';bash" $TitleOpt "perception" \
            --tab -e "bash -c 'sleep 15; $LOG_ENV && $BASHRC && $CHEJI';bash" $TitleOpt "cheji" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LOCAL_PLANNER';bash" $TitleOpt "local_planner" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $HAD_MAP';bash" $TitleOpt "had_map" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $GUARDIAN';bash" $TitleOpt "guardian" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $OPERATOR_TOOL';bash" $TitleOpt "operator_tool" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $TRACK_RECORDER';bash" $TitleOpt "track_recorder" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $HADMAP_ENGINE';bash" $TitleOpt "hadmap_engine" \
            --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $RECORD_CACHE';bash" $TitleOpt "record_cache" \
            --tab -e "bash -c 'sleep 2';bash";
    elif [ "$VehicleType" == "jinlv" ];then
        $GuiTerminal  --window -e "bash -c '$LOG_ENV && $BASHRC && $ROSCORE';bash" $TitleOpt "core" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $LOCALIZATION';bash" $TitleOpt "localization" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LIDAR_CAMERA_DRIVERS';bash" $TitleOpt "drivers"  \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $JINLV_CAN_ADAPTER';bash" $TitleOpt "canadapter"  \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $JINLV_CONTROLLER';bash" $TitleOpt "controller"  \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $PERCEPTION';bash" $TitleOpt "perception" \
            --tab -e "bash -c 'sleep 15; $LOG_ENV && $BASHRC && $CHEJI';bash" $TitleOpt "cheji" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LOCAL_PLANNER';bash" $TitleOpt "local_planner" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $HAD_MAP';bash" $TitleOpt "had_map" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $GUARDIAN';bash" $TitleOpt "guardian" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $OPERATOR_TOOL';bash" $TitleOpt "operator_tool" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $TRACK_RECORDER';bash" $TitleOpt "track_recorder" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $HADMAP_ENGINE';bash" $TitleOpt "hadmap_engine" \
            --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $RECORD_CACHE';bash" $TitleOpt "record_cache" \
            --tab -e "bash -c 'sleep 2';bash";
    elif [ "$VehicleType" == "byd" ];then
        $GuiTerminal  --window -e "bash -c '$LOG_ENV && $BASHRC && $ROSCORE';bash" $TitleOpt "core" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $LOCALIZATION';bash" $TitleOpt "localization" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $BYD_CAN_ADAPTER';bash" $TitleOpt "canadapter"  \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LIDAR_CAMERA_DRIVERS';bash" $TitleOpt "drivers"  \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $BYD_CONTROLLER';bash" $TitleOpt "controller"  \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $PERCEPTION';bash" $TitleOpt "perception" \
            --tab -e "bash -c 'sleep 15; $LOG_ENV && $BASHRC && $CHEJI';bash" $TitleOpt "cheji" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LOCAL_PLANNER';bash" $TitleOpt "local_planner" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $HAD_MAP';bash" $TitleOpt "had_map" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $GUARDIAN';bash" $TitleOpt "guardian" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $OPERATOR_TOOL';bash" $TitleOpt "operator_tool" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $TRACK_RECORDER';bash" $TitleOpt "track_recorder" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $HADMAP_ENGINE';bash" $TitleOpt "hadmap_engine" \
            --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $RECORD_CACHE';bash" $TitleOpt "record_cache" \
            --tab -e "bash -c 'sleep 2';bash";
    elif [ "$VehicleType" == "df" ];then
        $GuiTerminal  --window -e "bash -c '$LOG_ENV && $BASHRC && $ROSCORE';bash" $TitleOpt "core" \
            --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $LOCALIZATION';bash" $TitleOpt "localization" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $DONGFENG_CAN_ADAPTER';bash" $TitleOpt "canadapter"  \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $LIDAR_CAMERA_DRIVERS';bash" $TitleOpt "drivers"  \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $DONGFENG_CONTROLLER';bash" $TitleOpt "controller"  \
            --tab -e "bash -c 'sleep 7; $LOG_ENV && $BASHRC && $PERCEPTION';bash" $TitleOpt "perception" \
            --tab -e "bash -c 'sleep 15; $LOG_ENV && $BASHRC && $CHEJI';bash" $TitleOpt "cheji" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LOCAL_PLANNER';bash" $TitleOpt "local_planner" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $HAD_MAP';bash" $TitleOpt "had_map" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $GUARDIAN';bash" $TitleOpt "guardian" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $OPERATOR_TOOL';bash" $TitleOpt "operator_tool" \
            --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $TRACK_RECORDER';bash" $TitleOpt "track_recorder" \
            --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $HADMAP_ENGINE';bash" $TitleOpt "hadmap_engine" \
            --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $RECORD_CACHE';bash" $TitleOpt "record_cache" \
            --tab -e "bash -c 'sleep 2';bash";
    else
        echo "undefined vehicle type"
    fi
}

# silence mode will not display log on terminal
start_node_silence(){
    echo "start_node_silence"
    if [ "$VehicleType" == "wey" ]; then
        roscore 1>>${ROS_LOG_DIR}/roscore.log 2>>${ROS_LOG_DIR}/roscore.err &
        sleep 2 && roslaunch guardian system_guardian.launch 1>>${ROS_LOG_DIR}/system_guardian.launch.log 2>>${ROS_LOG_DIR}/system_guardian.launch.err &
        # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
        sleep 3 && roslaunch localization localization.launch 1>>${ROS_LOG_DIR}/localization.launch.log 2>>${ROS_LOG_DIR}/localization.launch.err &
        sleep 3 && roslaunch can_adapter vv6_can_adapter.launch 1>>${ROS_LOG_DIR}/vv6_can_adapter.launch.log 2>>${ROS_LOG_DIR}/vv6_can_adapter.launch.err &
        sleep 3 && roslaunch launch drivers.launch 1>>${ROS_LOG_DIR}/drivers.launch.log 2>>${ROS_LOG_DIR}/drivers.launch.err &
        sleep 2 && roslaunch controller controller_vv6.launch 1>>${ROS_LOG_DIR}/controller_vv6.launch.log 2>>${ROS_LOG_DIR}/controller_vv6.launch.err &
        sleep 3 && roslaunch launch perception.launch 1>>${ROS_LOG_DIR}/perception.launch.log 2>>${ROS_LOG_DIR}/perception.launch.err &
        sleep 15 && roslaunch telematics telematics.launch 1>>${ROS_LOG_DIR}/telematics.launch.log 2>>${ROS_LOG_DIR}/telematics.launch.err &
        sleep 2 && roslaunch launch local_planning.launch 1>>${ROS_LOG_DIR}/local_planning.launch.log 2>>${ROS_LOG_DIR}/local_planning.launch.err &
        sleep 2 && roslaunch launch hadmap.launch 1>>${ROS_LOG_DIR}/hadmap.launch.log 2>>${ROS_LOG_DIR}/hadmap.launch.err &
        sleep 2 && roslaunch track_recorder track_recorder.launch 1>>${ROS_LOG_DIR}/track_recorder.launch.log 2>>${ROS_LOG_DIR}/track_recorder.launch.err &
        sleep 5 && roslaunch record_cache record_cache.launch 1>>${ROS_LOG_DIR}/record_cache.launch.log 2>>${ROS_LOG_DIR}/record_cache.launch.err &
        sleep 3 && roslaunch hadmap_engine hadmap_engine.launch 1>>${ROS_LOG_DIR}/hadmap_engine.launch.log 2>>${ROS_LOG_DIR}/hadmap_engine.launch.err &
        sleep 2
    elif [ "$VehicleType" == "df" ]; then
        roscore 1>>${ROS_LOG_DIR}/roscore.log 2>>${ROS_LOG_DIR}/roscore.err &
        sleep 2 && roslaunch guardian system_guardian.launch 1>>${ROS_LOG_DIR}/system_guardian.launch.log 2>>${ROS_LOG_DIR}/system_guardian.launch.err &
        # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
        sleep 5 && roslaunch localization localization.launch 1>>${ROS_LOG_DIR}/localization.launch.log 2>>${ROS_LOG_DIR}/localization.launch.err &
        sleep 3 && roslaunch can_adapter DongFeng_E70_can_adapter.launch 1>>${ROS_LOG_DIR}/DongFeng_E70_can_adapter.launch.log 2>>${ROS_LOG_DIR}/DongFeng_E70_can_adapter.launch.err &
        sleep 3 && roslaunch launch drivers.launch 1>>${ROS_LOG_DIR}/drivers.launch.log 2>>${ROS_LOG_DIR}/drivers.launch.err &
        sleep 2 && roslaunch controller controller_dfe70.launch 1>>${ROS_LOG_DIR}/controller_dfe70.launch.log 2>>${ROS_LOG_DIR}/controller_dfe70.launch.err &
        sleep 7 && roslaunch launch perception.launch 1>>${ROS_LOG_DIR}/perception.launch.log 2>>${ROS_LOG_DIR}/perception.launch.err &
        sleep 15 && roslaunch telematics telematics.launch 1>>${ROS_LOG_DIR}/telematics.launch.log 2>>${ROS_LOG_DIR}/telematics.launch.err &
        sleep 2 && roslaunch launch local_planning.launch 1>>${ROS_LOG_DIR}/local_planning.launch.log 2>>${ROS_LOG_DIR}/local_planning.launch.err &
        sleep 2 && roslaunch launch hadmap.launch 1>>${ROS_LOG_DIR}/hadmap.launch.log 2>>${ROS_LOG_DIR}/hadmap.launch.err &
        sleep 2 && roslaunch track_recorder track_recorder.launch 1>>${ROS_LOG_DIR}/track_recorder.launch.log 2>>${ROS_LOG_DIR}/track_recorder.launch.err &
        sleep 5 && roslaunch record_cache record_cache.launch 1>>${ROS_LOG_DIR}/record_cache.launch.log 2>>${ROS_LOG_DIR}/record_cache.launch.err &
        sleep 3 && roslaunch hadmap_engine hadmap_engine.launch 1>>${ROS_LOG_DIR}/hadmap_engine.launch.log 2>>${ROS_LOG_DIR}/hadmap_engine.launch.err &
        sleep 2
    elif [ "$VehicleType" == "jinlv" ]; then
        roscore 1>>${ROS_LOG_DIR}/roscore.log 2>>${ROS_LOG_DIR}/roscore.err &
        sleep 2 && roslaunch guardian system_guardian.launch 1>>${ROS_LOG_DIR}/system_guardian.launch.log 2>>${ROS_LOG_DIR}/system_guardian.launch.err &
        # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
        sleep 3 && roslaunch localization localization.launch 1>>${ROS_LOG_DIR}/localization.launch.log 2>>${ROS_LOG_DIR}/localization.launch.err &
        sleep 3 && roslaunch can_adapter jinlv_can_adapter.launch 1>>${ROS_LOG_DIR}/jinlv_can_adapter.launch.log 2>>${ROS_LOG_DIR}/jinlv_can_adapter.launch.err &
        sleep 3 && roslaunch launch drivers.launch 1>>${ROS_LOG_DIR}/drivers.launch.log 2>>${ROS_LOG_DIR}/drivers.launch.err &
        sleep 2 && roslaunch controller controller_jinlv.launch 1>>${ROS_LOG_DIR}/controller_jinlv.launch.log 2>>${ROS_LOG_DIR}/controller_jinlv.launch.err &
        sleep 3 && roslaunch launch perception.launch 1>>${ROS_LOG_DIR}/perception.launch.log 2>>${ROS_LOG_DIR}/perception.launch.err &
        sleep 15 && roslaunch telematics telematics.launch 1>>${ROS_LOG_DIR}/telematics.launch.log 2>>${ROS_LOG_DIR}/telematics.launch.err &
        sleep 2 && roslaunch launch local_planning.launch 1>>${ROS_LOG_DIR}/local_planning.launch.log 2>>${ROS_LOG_DIR}/local_planning.launch.err &
        sleep 2 && roslaunch launch hadmap.launch 1>>${ROS_LOG_DIR}/hadmap.launch.log 2>>${ROS_LOG_DIR}/hadmap.launch.err &
        sleep 2 && roslaunch track_recorder track_recorder.launch 1>>${ROS_LOG_DIR}/track_recorder.launch.log 2>>${ROS_LOG_DIR}/track_recorder.launch.err &
        sleep 5 && roslaunch record_cache record_cache.launch 1>>${ROS_LOG_DIR}/record_cache.launch.log 2>>${ROS_LOG_DIR}/record_cache.launch.err &
        sleep 3 && roslaunch hadmap_engine hadmap_engine.launch 1>>${ROS_LOG_DIR}/hadmap_engine.launch.log 2>>${ROS_LOG_DIR}/hadmap_engine.launch.err &
        sleep 2
    elif [ "$VehicleType" == "byd" ]; then
        roscore 1>>${ROS_LOG_DIR}/roscore.log 2>>${ROS_LOG_DIR}/roscore.err &
        sleep 2 && roslaunch guardian system_guardian.launch 1>>${ROS_LOG_DIR}/system_guardian.launch.log 2>>${ROS_LOG_DIR}/system_guardian.launch.err &
        # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
        sleep 3 && roslaunch localization localization.launch 1>>${ROS_LOG_DIR}/localization.launch.log 2>>${ROS_LOG_DIR}/localization.launch.err &
        sleep 3 && roslaunch can_adapter byd_can_adapter.launch 1>>${ROS_LOG_DIR}/byd_can_adapter.launch.log 2>>${ROS_LOG_DIR}/byd_can_adapter.launch.err &
        sleep 2 && roslaunch launch drivers.launch 1>>${ROS_LOG_DIR}/drivers.launch.log 2>>${ROS_LOG_DIR}/drivers.launch.err &
        sleep 2 && roslaunch controller controller_qinpro.launch 1>>${ROS_LOG_DIR}/controller_qinpro.launch.log 2>>${ROS_LOG_DIR}/controller_qinpro.launch.err &
        sleep 3 && roslaunch launch perception.launch 1>>${ROS_LOG_DIR}/perception.launch.log 2>>${ROS_LOG_DIR}/perception.launch.err &
        sleep 15 && roslaunch telematics telematics.launch 1>>${ROS_LOG_DIR}/telematics.launch.log 2>>${ROS_LOG_DIR}/telematics.launch.err &
        sleep 2 && roslaunch launch local_planning.launch 1>>${ROS_LOG_DIR}/local_planning.launch.log 2>>${ROS_LOG_DIR}/local_planning.launch.err &
        sleep 2 && roslaunch launch hadmap.launch 1>>${ROS_LOG_DIR}/hadmap.launch.log 2>>${ROS_LOG_DIR}/hadmap.launch.err &
        sleep 2 && roslaunch track_recorder track_recorder.launch 1>>${ROS_LOG_DIR}/track_recorder.launch.log 2>>${ROS_LOG_DIR}/track_recorder.launch.err &
        sleep 5 && roslaunch record_cache record_cache.launch 1>>${ROS_LOG_DIR}/record_cache.launch.log 2>>${ROS_LOG_DIR}/record_cache.launch.err &
        sleep 3 && roslaunch hadmap_engine hadmap_engine.launch 1>>${ROS_LOG_DIR}/hadmap_engine.launch.log 2>>${ROS_LOG_DIR}/hadmap_engine.launch.err &
        sleep 2
    else
        echo "undefined vehicle type"
    fi
}

# main
echo $VehicleType  #wey|byd|jinlv|df
echo $GuiServer  #background|xfce4|gnome
echo $RunMode  #normal|debug

export GuiTerminal
export TitleOpt

core_pid=`ps aux | grep -v grep | grep "roscore$" |awk '{print $2}'`
if [ ! -z "$core_pid" ];then
    rosnode kill -a
    kill $core_pid
fi

# 需要在run.sh中将/dev/ttyACM0 /dev/video* /dev/ttyUSB*权限设置为777
# echo "123"|sudo -S chmod +777 /dev -R 
###########################################################
export GLOG_logtostderr=1
export GLOG_colorlogtostderr=1

# [[ ! -d $ROS_LOG_DIR ]] && mkdir -p $ROS_LOG_DIR
find /home/mogo/data/log -mtime +3 -name *.log -exec rm -Rf {} \;

export LOG_ENV="export GLOG_logtostderr=1; export GLOG_colorlogtostderr=1; export ROS_LOG_DIR=${ROS_LOG_DIR}"
echo "LOG_ENV:$LOG_ENV"
##########################################################
ROSCORE="roscore 2>&1 | tee \${ROS_LOG_DIR}/roscore.log"
LOCALIZATION="roslaunch localization localization.launch 2>&1 | tee -i \${ROS_LOG_DIR}/localization.launch.log"
VV6_CAN_ADAPTER="roslaunch can_adapter vv6_can_adapter.launch 2>&1 | tee -i \${ROS_LOG_DIR}/vv6_can_adapter.launch.log"
BYD_CAN_ADAPTER="roslaunch can_adapter byd_can_adapter.launch 2>&1 | tee -i \${ROS_LOG_DIR}/byd_can_adapter.launch.log"
JINLV_CAN_ADAPTER="roslaunch can_adapter jinlv_can_adapter.launch 2>&1 | tee -i \${ROS_LOG_DIR}/jinlv_can_adapter.launch.log"
DONGFENG_CAN_ADAPTER="roslaunch can_adapter DongFeng_E70_can_adapter.launch 2>&1 | tee -i \${ROS_LOG_DIR}/DongFeng_E70_can_adapter.launch.log"
VV6_CONTROLLER="roslaunch controller controller_vv6.launch 2>&1 | tee -i \${ROS_LOG_DIR}/controller_vv6.launch.log"
BYD_CONTROLLER="roslaunch controller controller_qinpro.launch 2>&1 | tee -i \${ROS_LOG_DIR}/controller_qinpro.launch.log"
JINLV_CONTROLLER="roslaunch controller controller_jinlv.launch 2>&1 | tee -i \${ROS_LOG_DIR}/controller_jinlv.launch.log"
DONGFENG_CONTROLLER="roslaunch controller controller_dfe70.launch 2>&1 | tee -i \${ROS_LOG_DIR}/controller_dfe70.launch.log"
PERCEPTION="roslaunch launch perception.launch 2>&1 | tee -i \${ROS_LOG_DIR}/perception.launch.log"
CHEJI="roslaunch telematics telematics.launch 2>&1 | tee -i \${ROS_LOG_DIR}/telematics.launch.log"
LOCAL_PLANNER="roslaunch launch local_planning.launch 2>&1 | tee -i \${ROS_LOG_DIR}/local_planning.launch.log"
HAD_MAP="roslaunch launch hadmap.launch 2>&1 | tee -i \${ROS_LOG_DIR}/hadmap.launch.log"
LIDAR_CAMERA_DRIVERS="roslaunch launch drivers.launch 2>&1 | tee -i \${ROS_LOG_DIR}/drivers.launch.log"
OPERATOR_TOOL="roslaunch operator_tool operator_tool.launch 2>&1 | tee -i \${ROS_LOG_DIR}/operator_tool.launch.log"
GUARDIAN="roslaunch guardian system_guardian.launch 2>&1 | tee -i \${ROS_LOG_DIR}/system_guardian.launch.log"
TRACK_RECORDER="roslaunch track_recorder track_recorder.launch 2>&1 | tee -i \${ROS_LOG_DIR}/track_recorder.launch.log"
RECORD_CACHE="roslaunch record_cache record_cache.launch 2>&1 | tee -i \${ROS_LOG_DIR}/record_cache.launch.log"
HADMAP_ENGINE="roslaunch hadmap_engine hadmap_engine.launch 2>&1 | tee -i \${ROS_LOG_DIR}/hadmap_engine.launch.log"
##########################################################


if [ "$GuiServer" = "x" ];then
    GuiTerminal="/usr/bin/xfce4-terminal"
    TitleOpt="-T"
elif [ "$GuiServer" = "g" ];then
    GuiTerminal="/usr/bin/gnome-terminal"
    TitleOpt="-t"
else
    echo "GuiServer is $GuiServer"
fi


if [ "$GuiServer" == "x" -o "$GuiServer" == "g" ];then
    start_node_terminal
fi

if [ "$GuiServer" == "silence" ];then
    if [ $RunMode -eq 1 ];then 
	export GLOG_logtostderr=1
	export export GLOG_colorlogtostderr=1
	source $SETUP_ROS
	source $SETUP_AUTOPILOT
        start_node_silence
    else
        echo "nodes can't be launch with silence mode in catkin_ws environment,please use silence mode in docker's autopilot environment"
    fi
fi
