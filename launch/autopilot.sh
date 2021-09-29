#!/bin/bash

# GuiServer:
# silence -- 后台启动
# xfce4 -- docker中启动 终端使用xfce4-terminal
# gnome -- 宿主机中启动 终端使用gnome-terminal
export GuiServer=$2
# VehicleType    wey jinlv byd df ...
export VehicleType=$1
# RunMode    1:autopilot    2:catkin_ws
export RunMode
export ABS_PATH

export SETUP_ROS
export SETUP_AUTOPILOT

if [ -z "$VehicleType" ];then
    echo "Vehicle type is not defined,exit."
    exit 0
fi

if [ "$GuiServer" = "" ]; then
    GuiServer="silence"
fi

export DATE=`date +"%Y%m%d"`
export TIME=`date +"%H%M%S"`
export ROS_LOG_DIR=/home/mogo/data/log/${DATE}_${TIME}
[[ ! -d $ROS_LOG_DIR ]] && mkdir -p $ROS_LOG_DIR

# autopilot:/home/mogo/autopilot/share/launch
# catkin_ws:/home/mogo/data/catkin_ws/src/system/launch
# script_path=$(readlink -f $0)
# ABS_PATH=$(dirname $script_path)
ABS_PATH="$(cd "$(dirname $0)" && pwd)"
RunMode=$(echo $ABS_PATH | grep -w "/home/mogo/autopilot" | wc -l)

SETUP_ROS="/opt/ros/melodic/setup.bash"

if [ $RunMode -eq 0 ];then
    SETUP_AUTOPILOT="$ABS_PATH/../../../devel/setup.bash"
elif [ $RunMode -eq 1 ];then
    SETUP_AUTOPILOT="$ABS_PATH/../../setup.bash"
else
    echo "RunMode is $RunMode"
fi
echo $ABS_PATH

export BASHRC="source ${SETUP_ROS} && source ${SETUP_AUTOPILOT}"
/bin/bash $ABS_PATH/integration.sh > /home/mogo/data/log/integration.log
