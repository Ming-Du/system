#!/bin/bash

Usage(){
    echo "Usage:"
    echo "`basename $0` <wey|byd|jinlv|df> [silence|x|g]"
    echo "Options:"
    echo "wey        --长城车"
    echo "byd        --byd车"
    echo "jinlv      --小巴车"
    echo "df         --东风车"
    echo "silence    --后台启动[默认值]"
    echo "x          --xfce4窗口启动"
    echo "g          --gnome窗口启动"
}


check_env(){
    #add environment to /root/.bashrc
    env_roshostname_root=$(grep  "export\b[[:space:]]*ROS_HOSTNAME"  /root/.bashrc | grep -v "^#")
    if [ -z "$env_roshostname_root" ];then
        echo "export ROS_HOSTNAME=$ros_machine" >> /root/.bashrc
    fi
    env_rosmasteruri_root=$(grep  "export\b[[:space:]]*ROS_MASTER_URI"  /root/.bashrc | grep -v "^#")
    if [ -z "$env_rosmasteruri_root" ];then
        echo "export ROS_MASTER_URI=http://$ros_master:11311" >> /root/.bashrc
    fi
    #add environment to /home/mogo/.bashrc
    env_roshostname_mogo=$(grep  "export\b[[:space:]]*ROS_HOSTNAME"  /home/mogo/.bashrc | grep -v "^#")
    if [ -z "$env_roshostname_mogo" ];then
        echo "export ROS_HOSTNAME=$ros_machine" >> /home/mogo/.bashrc
    fi
    env_rosmasteruri_mogo=$(grep  "export\b[[:space:]]*ROS_MASTER_URI"  /home/mogo/.bashrc | grep -v "^#")
    if [ -z "$env_rosmasteruri_mogo" ];then
        echo "export ROS_MASTER_URI=http://$ros_master:11311" >> /home/mogo/.bashrc
    fi
}
# vehicle/drivers/camera/camera.launch
# vehicle/drivers/lidar/lidar.launch
# vehicle/drivers/gnss/gnss.launch

#vehicle/perception/camera/perception_camera.launch
#vehicle/perception/lidar/perception_lidar.launch
#vehicle/perception/fusion/perception_fusion.launch

start_node_terminal_multi(){
    Logging "start_node_terminal_multi"
    # echo "func::GuiTerminal:$GuiTerminal"
    # echo "func::TitleOpt:$TitleOpt"
    if [ "$ros_machine" = "rosmaster" ];then
        #ros core
        $GuiTerminal --tab -e "bash -c '$LOG_ENV && $BASHRC && $ROSCORE';bash" $TitleOpt "core" &
        sleep 1
        #node 
        $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $LOCALIZATION';bash" $TitleOpt "localization" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $GNSS_DRIVERS';bash" $TitleOpt "gnss_drivers"  &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $CAMERA_DRIVER';bash" $TitleOpt "camera_drivers"  &
        $GuiTerminal --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $PERCEPTION_CAMERA';bash" $TitleOpt "perception_camera" &
        $GuiTerminal --tab -e "bash -c 'sleep 15; $LOG_ENV && $BASHRC && $CHEJI';bash" $TitleOpt "cheji" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LOCAL_PLANNER';bash" $TitleOpt "local_planner" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $HAD_MAP';bash" $TitleOpt "had_map" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $GUARDIAN';bash" $TitleOpt "guardian" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $OPERATOR_TOOL';bash" $TitleOpt "operator_tool" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $TRACK_RECORDER';bash" $TitleOpt "track_recorder" &
        $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $HADMAP_ENGINE';bash" $TitleOpt "hadmap_engine" &
        $GuiTerminal --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $RECORD_CACHE';bash" $TitleOpt "record_cache" &
        if [ "$VehicleType" == "wey" ];then
            $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $VV6_CAN_ADAPTER';bash" $TitleOpt "canadapter" &
            $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $VV6_CONTROLLER';bash" $TitleOpt "controller" &
        elif [ "$VehicleType" == "jinlv" ];then
            $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $JINLV_CAN_ADAPTER';bash" $TitleOpt "canadapter" &
            $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $JINLV_CONTROLLER';bash" $TitleOpt "controller" &
        elif [ "$VehicleType" == "byd" ];then
            $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $BYD_CAN_ADAPTER';bash" $TitleOpt "canadapter" &
            $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $BYD_CONTROLLER';bash" $TitleOpt "controller" &
        elif [ "$VehicleType" == "df" ];then
            $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $DONGFENG_CAN_ADAPTER';bash" $TitleOpt "canadapter" &
            $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $DONGFENG_CONTROLLER';bash" $TitleOpt "controller" &
        else
            Logging "undefined vehicle type"
        fi   
    else
        $GuiTerminal --tab -e "bash -c 'sleep 7; $LOG_ENV && $BASHRC && $PERCEPTION_FUSION';bash" $TitleOpt "perception_fusion" &
        sleep 1
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LIDAR_DRIVERS';bash" $TitleOpt "drivers_lidar"  &
        $GuiTerminal --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $PERCEPTION_LIDAR';bash" $TitleOpt "perception_lidar" &
    fi
}


# silence mode will not display log on terminal
start_node_silence_multi(){
    Logging "start_node_silence_multi"
    if [ "$ros_machine" = "rosmaster" ];then
        #ros core
        roscore 1>>${ROS_LOG_DIR}/roscore.log 2>>${ROS_LOG_DIR}/roscore.err &
        #node
        sleep 3 && roslaunch --wait $ABS_PATH/../config/vehicle/drivers/camera/camera.launch 1>>${ROS_LOG_DIR}/camera_drivers.launch.log 2>>${ROS_LOG_DIR}/camera_drivers.launch.err &
        sleep 2 && roslaunch --wait $ABS_PATH/../config/vehicle/drivers/gnss/gnss.launch 1>>${ROS_LOG_DIR}/gnss_drivers.launch.log 2>>${ROS_LOG_DIR}/gnss_drivers.launch.err &
        sleep 2 && roslaunch --wait guardian system_guardian.launch 1>>${ROS_LOG_DIR}/system_guardian.launch.log 2>>${ROS_LOG_DIR}/system_guardian.launch.err &
        sleep 5 && roslaunch --wait localization localization.launch 1>>${ROS_LOG_DIR}/localization.launch.log 2>>${ROS_LOG_DIR}/localization.launch.err &
        sleep 15 && roslaunch --wait telematics telematics.launch 1>>${ROS_LOG_DIR}/telematics.launch.log 2>>${ROS_LOG_DIR}/telematics.launch.err &
        sleep 2 && roslaunch --wait launch local_planning.launch 1>>${ROS_LOG_DIR}/local_planning.launch.log 2>>${ROS_LOG_DIR}/local_planning.launch.err &
        sleep 2 && roslaunch --wait launch hadmap.launch 1>>${ROS_LOG_DIR}/hadmap.launch.log 2>>${ROS_LOG_DIR}/hadmap.launch.err &
        sleep 2 && roslaunch --wait track_recorder track_recorder.launch 1>>${ROS_LOG_DIR}/track_recorder.launch.log 2>>${ROS_LOG_DIR}/track_recorder.launch.err &
        sleep 5 && roslaunch --wait record_cache record_cache.launch 1>>${ROS_LOG_DIR}/record_cache.launch.log 2>>${ROS_LOG_DIR}/record_cache.launch.err &
        sleep 3 && roslaunch --wait hadmap_engine hadmap_engine.launch 1>>${ROS_LOG_DIR}/hadmap_engine.launch.log 2>>${ROS_LOG_DIR}/hadmap_engine.launch.err &
        sleep 5 && roslaunch --wait $ABS_PATH/../config/vehicle/perception/camera/perception_camera.launch 1>>${ROS_LOG_DIR}/perception_camera.launch.log 2>>${ROS_LOG_DIR}/perception_camera.launch.err &
        if [ "$VehicleType" == "wey" ]; then
            # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
            sleep 3 && roslaunch --wait can_adapter vv6_can_adapter.launch 1>>${ROS_LOG_DIR}/vv6_can_adapter.launch.log 2>>${ROS_LOG_DIR}/vv6_can_adapter.launch.err &
            sleep 2 && roslaunch --wait controller controller_vv6.launch 1>>${ROS_LOG_DIR}/controller_vv6.launch.log 2>>${ROS_LOG_DIR}/controller_vv6.launch.err &
        elif [ "$VehicleType" == "df" ]; then
            # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
            sleep 3 && roslaunch --wait can_adapter DongFeng_E70_can_adapter.launch 1>>${ROS_LOG_DIR}/DongFeng_E70_can_adapter.launch.log 2>>${ROS_LOG_DIR}/DongFeng_E70_can_adapter.launch.err &
            sleep 2 && roslaunch --wait controller controller_dfe70.launch 1>>${ROS_LOG_DIR}/controller_dfe70.launch.log 2>>${ROS_LOG_DIR}/controller_dfe70.launch.err &
        elif [ "$VehicleType" == "jinlv" ]; then
            # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
            sleep 3 && roslaunch --wait can_adapter jinlv_can_adapter.launch 1>>${ROS_LOG_DIR}/jinlv_can_adapter.launch.log 2>>${ROS_LOG_DIR}/jinlv_can_adapter.launch.err &
            sleep 2 && roslaunch --wait controller controller_jinlv.launch 1>>${ROS_LOG_DIR}/controller_jinlv.launch.log 2>>${ROS_LOG_DIR}/controller_jinlv.launch.err &
        elif [ "$VehicleType" == "byd" ]; then
            # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
            sleep 3 && roslaunch --wait can_adapter byd_can_adapter.launch 1>>${ROS_LOG_DIR}/byd_can_adapter.launch.log 2>>${ROS_LOG_DIR}/byd_can_adapter.launch.err &
            sleep 2 && roslaunch --wait controller controller_qinpro.launch 1>>${ROS_LOG_DIR}/controller_qinpro.launch.log 2>>${ROS_LOG_DIR}/controller_qinpro.launch.err &
        else
            Logging "undefined vehicle type"
        fi
    else 
        sleep 2 && roslaunch --wait $ABS_PATH/../config/vehicle/drivers/lidar/lidar.launch 1>>${ROS_LOG_DIR}/lidar.launch.log 2>>${ROS_LOG_DIR}/lidar.launch.err &
        sleep 5 && roslaunch --wait $ABS_PATH/../config/vehicle/perception/lidar/perception_lidar.launch 1>>${ROS_LOG_DIR}/perception_lidar.launch.log 2>>${ROS_LOG_DIR}/perception_lidar.launch.err &
        sleep 7 && roslaunch --wait $ABS_PATH/../config/vehicle/perception/fusion/perception_fusion.launch 1>>${ROS_LOG_DIR}/perception_fusion.launch.log 2>>${ROS_LOG_DIR}/perception_fusion.launch.err &
    fi 
    sleep 17
}


start_node_terminal(){
    Logging "start_node_terminal"
    $GuiTerminal --tab -e "bash -c '$LOG_ENV && $BASHRC && $ROSCORE';bash" $TitleOpt "core" &
    sleep 1
    $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $LOCALIZATION';bash" $TitleOpt "localization" &
    $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $GNSS_DRIVERS';bash" $TitleOpt "gnss_drivers"  &
    $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $CAMERA_DRIVER';bash" $TitleOpt "camera_drivers"  &
    $GuiTerminal --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $PERCEPTION_CAMERA';bash" $TitleOpt "perception_camera" &
    $GuiTerminal --tab -e "bash -c 'sleep 15; $LOG_ENV && $BASHRC && $CHEJI';bash" $TitleOpt "cheji" &
    $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LOCAL_PLANNER';bash" $TitleOpt "local_planner" &
    $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $HAD_MAP';bash" $TitleOpt "had_map" &
    $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $GUARDIAN';bash" $TitleOpt "guardian" &
    $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $OPERATOR_TOOL';bash" $TitleOpt "operator_tool" &
    $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $TRACK_RECORDER';bash" $TitleOpt "track_recorder" &
    $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $HADMAP_ENGINE';bash" $TitleOpt "hadmap_engine" &
    $GuiTerminal --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $RECORD_CACHE';bash" $TitleOpt "record_cache" &
    $GuiTerminal --tab -e "bash -c 'sleep 7; $LOG_ENV && $BASHRC && $PERCEPTION_FUSION';bash" $TitleOpt "perception_fusion" &
    $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $LIDAR_DRIVERS';bash" $TitleOpt "drivers_lidar"  &
    $GuiTerminal --tab -e "bash -c 'sleep 5; $LOG_ENV && $BASHRC && $PERCEPTION_LIDAR';bash" $TitleOpt "perception_lidar" &
    if [ "$VehicleType" == "wey" ];then
        $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $VV6_CAN_ADAPTER';bash" $TitleOpt "canadapter" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $VV6_CONTROLLER';bash" $TitleOpt "controller" &
    elif [ "$VehicleType" == "jinlv" ];then
        $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $JINLV_CAN_ADAPTER';bash" $TitleOpt "canadapter" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $JINLV_CONTROLLER';bash" $TitleOpt "controller" &
    elif [ "$VehicleType" == "byd" ];then
        $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $BYD_CAN_ADAPTER';bash" $TitleOpt "canadapter" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $BYD_CONTROLLER';bash" $TitleOpt "controller" &
    elif [ "$VehicleType" == "df" ];then
        $GuiTerminal --tab -e "bash -c 'sleep 3; $LOG_ENV && $BASHRC && $DONGFENG_CAN_ADAPTER';bash" $TitleOpt "canadapter" &
        $GuiTerminal --tab -e "bash -c 'sleep 2; $LOG_ENV && $BASHRC && $DONGFENG_CONTROLLER';bash" $TitleOpt "controller" &
    else
        Logging "undefined vehicle type"
    fi
}


# silence mode will not display log on terminal
start_node_silence(){
    Logging "start_node_silence"
    roscore 1>>${ROS_LOG_DIR}/roscore.log 2>>${ROS_LOG_DIR}/roscore.err &
    sleep 3 && roslaunch --wait launch drivers.launch 1>>${ROS_LOG_DIR}/drivers.launch.log 2>>${ROS_LOG_DIR}/drivers.launch.err &
    sleep 2 && roslaunch --wait guardian system_guardian.launch 1>>${ROS_LOG_DIR}/system_guardian.launch.log 2>>${ROS_LOG_DIR}/system_guardian.launch.err &
    sleep 5 && roslaunch --wait localization localization.launch 1>>${ROS_LOG_DIR}/localization.launch.log 2>>${ROS_LOG_DIR}/localization.launch.err &
    sleep 15 && roslaunch --wait telematics telematics.launch 1>>${ROS_LOG_DIR}/telematics.launch.log 2>>${ROS_LOG_DIR}/telematics.launch.err &
    sleep 2 && roslaunch --wait launch local_planning.launch 1>>${ROS_LOG_DIR}/local_planning.launch.log 2>>${ROS_LOG_DIR}/local_planning.launch.err &
    sleep 2 && roslaunch --wait launch hadmap.launch 1>>${ROS_LOG_DIR}/hadmap.launch.log 2>>${ROS_LOG_DIR}/hadmap.launch.err &
    sleep 2 && roslaunch --wait track_recorder track_recorder.launch 1>>${ROS_LOG_DIR}/track_recorder.launch.log 2>>${ROS_LOG_DIR}/track_recorder.launch.err &
    sleep 5 && roslaunch --wait record_cache record_cache.launch 1>>${ROS_LOG_DIR}/record_cache.launch.log 2>>${ROS_LOG_DIR}/record_cache.launch.err &
    sleep 3 && roslaunch --wait hadmap_engine hadmap_engine.launch 1>>${ROS_LOG_DIR}/hadmap_engine.launch.log 2>>${ROS_LOG_DIR}/hadmap_engine.launch.err &
    sleep 7 && roslaunch --wait launch perception.launch 1>>${ROS_LOG_DIR}/perception.launch.log 2>>${ROS_LOG_DIR}/perception.launch.err &
         
    if [ "$VehicleType" == "wey" ]; then
        # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
        sleep 3 && roslaunch --wait can_adapter vv6_can_adapter.launch 1>>${ROS_LOG_DIR}/vv6_can_adapter.launch.log 2>>${ROS_LOG_DIR}/vv6_can_adapter.launch.err &
        sleep 2 && roslaunch --wait controller controller_vv6.launch 1>>${ROS_LOG_DIR}/controller_vv6.launch.log 2>>${ROS_LOG_DIR}/controller_vv6.launch.err &
    elif [ "$VehicleType" == "df" ]; then
        # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
        sleep 3 && roslaunch --wait can_adapter DongFeng_E70_can_adapter.launch 1>>${ROS_LOG_DIR}/DongFeng_E70_can_adapter.launch.log 2>>${ROS_LOG_DIR}/DongFeng_E70_can_adapter.launch.err &
        sleep 2 && roslaunch --wait controller controller_dfe70.launch 1>>${ROS_LOG_DIR}/controller_dfe70.launch.log 2>>${ROS_LOG_DIR}/controller_dfe70.launch.err &
    elif [ "$VehicleType" == "jinlv" ]; then
        # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
        sleep 3 && roslaunch --wait can_adapter jinlv_can_adapter.launch 1>>${ROS_LOG_DIR}/jinlv_can_adapter.launch.log 2>>${ROS_LOG_DIR}/jinlv_can_adapter.launch.err &
        sleep 2 && roslaunch --wait controller controller_jinlv.launch 1>>${ROS_LOG_DIR}/controller_jinlv.launch.log 2>>${ROS_LOG_DIR}/controller_jinlv.launch.err &
    elif [ "$VehicleType" == "byd" ]; then
        # sleep 2 && roslaunch operator_tool operator_tool.launch 2>&1 | tee ${ROS_LOG_DIR}/operator_tool.launch.log &
        sleep 3 && roslaunch --wait can_adapter byd_can_adapter.launch 1>>${ROS_LOG_DIR}/byd_can_adapter.launch.log 2>>${ROS_LOG_DIR}/byd_can_adapter.launch.err &
        sleep 2 && roslaunch --wait controller controller_qinpro.launch 1>>${ROS_LOG_DIR}/controller_qinpro.launch.log 2>>${ROS_LOG_DIR}/controller_qinpro.launch.err &
    else
        Logging "undefined vehicle type"
    fi
    sleep 17
}

Logging(){
    datetime=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$datetime] $*"
    echo "[$datetime] $*" >> $LOGFILE
}
# main
LOGFILE="/home/mogo/data/log/autopilot-`date +"%Y%m%d%H%M%S"`.log"
if [ $# -eq 0 ];then 
    Logging "error:请指定车型"
    Usage
    exit 0
fi
Logging "command : $0 $@"

# GuiServer:
# silence -- 后台启动
# xfce4 -- docker中启动 终端使用xfce4-terminal
# gnome -- 宿主机中启动 终端使用gnome-terminal
export GuiServer=$2
# VehicleType    wey jinlv byd df ...
export VehicleType=$1
# RunMode    1:autopilot    0:catkin_ws
export RunMode # 运行方式  0：在catkin_ws环境中运行的debug模式  1：在autopilot环境中运行的release模式
export ABS_PATH # autopilot.sh脚本的路径

export GuiTerminal # 使用的terminal程序的绝对路径，如/usr/bin/xfce4-terminal
export TitleOpt # 指定terminal窗口标题的选项，xfce为'-T'，gnome为'-t'

export SETUP_ROS # ros系统自带的setup.bash路径，一般位于/opt/ros/melodic/setup.bash
export SETUP_AUTOPILOT # 用户程序的setup.bash

# autopilot:/home/mogo/autopilot/share/launch
# catkin_ws:/home/mogo/data/catkin_ws/src/system/launch
ABS_PATH="$(cd "$(dirname $0)" && pwd)"
RunMode=$(echo $ABS_PATH | grep -w "/home/mogo/autopilot" | wc -l)
SETUP_ROS="/opt/ros/melodic/setup.bash"

if [ $RunMode -eq 0 ];then
    SETUP_AUTOPILOT="$ABS_PATH/../../../devel/setup.bash"
    ROSCONSOLE_CONFIG_FILE="$ABS_PATH/../config/rosnodeInfo.config" 
elif [ $RunMode -eq 1 ];then
    SETUP_AUTOPILOT="$ABS_PATH/../../setup.bash"
    ROSCONSOLE_CONFIG_FILE="$ABS_PATH/../config/rosnodeErr.config" 
else
    Logging "RunMode is $RunMode"
fi
Logging "path : $ABS_PATH"

if [ "$VehicleType" != "wey" -a "$VehicleType" != "df" -a "$VehicleType" != "byd" -a "$VehicleType" != "jinlv" ];then
    Logging "error:不支持此车型。车型：$VehicleType"
    Usage
    exit 0
fi
export ros_master="localhost"
export xavier_type="single" #单xavier or 双xavier
export ros_machine="${ros_master}" #主机:rosmaster 从机:rosslave
# 判断是否为双Xavier
master_ip=$(cat /etc/hosts | grep -w rosmaster | grep -v "^#" | awk '{print $1}')
slave_ip=$(cat /etc/hosts | grep -w rosslave | grep -v "^#" | awk '{print $1}')
if [ -z "$master_ip" -o -z "$slave_ip" ];then
    xavier_type="single"
    ros_machine="titan-ubuntu1"
    ros_master=$ros_machine
else
    # xavier_type="multi"
    ethnet_ip=$(ifconfig eth0 | grep -Eo '([0-9]+[.]){3}[0-9]+'| grep -v "255")
    [[ -z "$ethnet_ip" ]] && Logging "ip address is null" && exit 1
    if [ "$master_ip" == "127.0.0.1" -o "$master_ip" == "$ethnet_ip" ];then
        ros_machine="rosmaster"
        ros_master=$ros_machine
        try_times=0
        while [ true ];do
            try_times=$((try_times + 1))
            ping -c 1 -W 2 $slave_ip > /dev/null
            if [ $? -eq 0 ];then #双xavier
                xavier_type="multi"
                check_env
                break
            else #try 5 times
                if [ $try_times -eq 5 ];then
                    Logging "double Xavier config has be set,but cannot contact with rosslave[$slave_ip],startup with single Xavier type"
                    xavier_type="single"
                    break
                else
                    Logging "cannot ping rosslave[$slave_ip],will try again after 3 seconds"
                    sleep 3
                    continue
                fi
            fi
        done
    else
        if [ "$ethnet_ip" == "$slave_ip" ];then
            ros_machine="rosslave"
            ros_master="rosmaster"
            while [ true ];do
                ping -c 1 -W 2 $master_ip > /dev/null
                if [ $? -eq 0 ];then #双xavier
                    xavier_type="multi"
                    check_env
                    break
                else #单Xavier
                    Logging "cannot contact with ${ros_master}[${master_ip}],will try again after 3 seconds"
                    sleep 3
                    continue;
                fi
            done
        else
            Logging "ip address is not matched with host,please check /etc/hosts or reset ip address"
            exit 1
        fi
    fi
fi

Logging "rosmachine:${ros_machine} rosmaster:${ros_master} xavier_type:${xavier_type}"

if [ "$GuiServer" = "x" ];then
    GuiTerminal="/usr/bin/xfce4-terminal"
    TitleOpt="-T"
elif [ "$GuiServer" = "g" ];then
    GuiTerminal="/usr/bin/gnome-terminal"
    TitleOpt="-t"
else
    GuiServer="silence"
    Logging "GuiServer is $GuiServer"
fi

# export DATE=`date +"%Y%m%d"`
# export TIME=`date +"%H%M%S"`
export GLOG_logtostderr=1
export GLOG_colorlogtostderr=1
export LOG_DIR="/home/mogo/data/log"
# ros日志存储路径的环境变量
export ROS_LOG_DIR="${LOG_DIR}/$(date +"%Y%m%d_%H")"
# ros日志配置文件的环境变量
export ROSCONSOLE_CONFIG_FILE
export ROS_HOSTNAME=${ros_machine}
export ROS_MASTER_URI=http://${ros_master}:11311
export LOG_ENV="export GLOG_logtostderr=1; export GLOG_colorlogtostderr=1; export ROS_LOG_DIR=${ROS_LOG_DIR}; export ROS_MASTER_URI=http://${ros_master}:11311; export ROS_HOSTNAME=${ros_machine}"
[[ ! -d $ROS_LOG_DIR ]] && mkdir -p $ROS_LOG_DIR
ln -snf $ROS_LOG_DIR ${LOG_DIR}/latest
Logging "ROS_LOG_DIR=$ROS_LOG_DIR"

core_pid=$(ps aux | grep -v grep | grep "roscore$" |awk '{print $2}')
if [ ! -z "$core_pid" ];then
    rosnode kill -a
    kill $core_pid
fi

find ${LOG_DIR} -maxdepth 1 -mtime +3 -type d -exec rm -Rf {} \;
find /home/mogo/data/bags/ -maxdepth 1 -mtime +1 -type d -exec rm -Rf {} \;
find /home/mogo/data/log -name "autopilot*.log" -mtime +1 -exec rm -Rf {} \;
##########################################################
ROSCORE="roscore 2>&1 | tee \${ROS_LOG_DIR}/roscore.log"
LOCALIZATION="roslaunch --wait localization localization.launch 2>&1 | tee -i \${ROS_LOG_DIR}/localization.launch.log"
VV6_CAN_ADAPTER="roslaunch --wait can_adapter vv6_can_adapter.launch 2>&1 | tee -i \${ROS_LOG_DIR}/vv6_can_adapter.launch.log"
BYD_CAN_ADAPTER="roslaunch --wait can_adapter byd_can_adapter.launch 2>&1 | tee -i \${ROS_LOG_DIR}/byd_can_adapter.launch.log"
JINLV_CAN_ADAPTER="roslaunch --wait can_adapter jinlv_can_adapter.launch 2>&1 | tee -i \${ROS_LOG_DIR}/jinlv_can_adapter.launch.log"
DONGFENG_CAN_ADAPTER="roslaunch --wait can_adapter DongFeng_E70_can_adapter.launch 2>&1 | tee -i \${ROS_LOG_DIR}/DongFeng_E70_can_adapter.launch.log"
VV6_CONTROLLER="roslaunch --wait controller controller_vv6.launch 2>&1 | tee -i \${ROS_LOG_DIR}/controller_vv6.launch.log"
BYD_CONTROLLER="roslaunch --wait controller controller_qinpro.launch 2>&1 | tee -i \${ROS_LOG_DIR}/controller_qinpro.launch.log"
JINLV_CONTROLLER="roslaunch --wait controller controller_jinlv.launch 2>&1 | tee -i \${ROS_LOG_DIR}/controller_jinlv.launch.log"
DONGFENG_CONTROLLER="roslaunch --wait controller controller_dfe70.launch 2>&1 | tee -i \${ROS_LOG_DIR}/controller_dfe70.launch.log"
CHEJI="roslaunch --wait telematics telematics.launch 2>\${ROS_LOG_DIR}/telematics.launch.log"
LOCAL_PLANNER="roslaunch --wait launch local_planning.launch 2>&1 | tee -i \${ROS_LOG_DIR}/local_planning.launch.log"
HAD_MAP="roslaunch --wait launch hadmap.launch 2>&1 | tee -i \${ROS_LOG_DIR}/hadmap.launch.log"
OPERATOR_TOOL="roslaunch --wait operator_tool operator_tool.launch 2>&1 | tee -i \${ROS_LOG_DIR}/operator_tool.launch.log"
GUARDIAN="roslaunch --wait guardian system_guardian.launch 2>&1 | tee -i \${ROS_LOG_DIR}/system_guardian.launch.log"
TRACK_RECORDER="roslaunch --wait track_recorder track_recorder.launch 2>&1 | tee -i \${ROS_LOG_DIR}/track_recorder.launch.log"
RECORD_CACHE="roslaunch --wait record_cache record_cache.launch 2>&1 | tee -i \${ROS_LOG_DIR}/record_cache.launch.log"
HADMAP_ENGINE="roslaunch --wait hadmap_engine hadmap_engine.launch 2>&1 | tee -i \${ROS_LOG_DIR}/hadmap_engine.launch.log"
LIDAR_CAMERA_DRIVERS="roslaunch launch drivers.launch 2>&1 | tee -i \${ROS_LOG_DIR}/drivers.launch.log"
PERCEPTION="roslaunch launch perception.launch 2>&1 | tee -i \${ROS_LOG_DIR}/perception.launch.log"
# detach from perception.launch
PERCEPTION_LIDAR="roslaunch --wait $ABS_PATH/../config/vehicle/perception/lidar/perception_lidar.launch 2>&1 | tee -i \${ROS_LOG_DIR}/perception_lidar.launch.log"
PERCEPTION_CAMERA="roslaunch --wait $ABS_PATH/../config/vehicle/perception/camera/perception_camera.launch 2>&1 | tee -i \${ROS_LOG_DIR}/perception_camera.launch.log"
PERCEPTION_FUSION="roslaunch --wait $ABS_PATH/../config/vehicle/perception/fusion/perception_fusion.launch 2>&1 | tee -i \${ROS_LOG_DIR}/perception_fusion.launch.log"
# detach from driver.launch
LIDAR_DRIVERS="roslaunch --wait $ABS_PATH/../config/vehicle/drivers/lidar/lidar.launch 2>&1 | tee -i \${ROS_LOG_DIR}/lidar_drivers.launch.log"
CAMERA_DRIVER="roslaunch --wait $ABS_PATH/../config/vehicle/drivers/camera/camera.launch 2>&1 | tee -i \${ROS_LOG_DIR}/camera_drivers.launch.log"
GNSS_DRIVERS="roslaunch --wait $ABS_PATH/../config/vehicle/drivers/gnss/gnss.launch 2>&1 | tee -i \${ROS_LOG_DIR}/gnss_drivers.launch.log"
##########################################################

export BASHRC="source ${SETUP_ROS} && source ${SETUP_AUTOPILOT}"

source $SETUP_ROS
source $SETUP_AUTOPILOT

if [ "$GuiServer" == "x" -o "$GuiServer" == "g" ];then
    if [ "$xavier_type" == "multi" ];then
        start_node_terminal_multi
    else
        start_node_terminal
    fi
fi

if [ "$GuiServer" == "silence" ];then
    if [ $RunMode -eq 1 ];then
        if [ "$xavier_type" == "multi" ];then
            start_node_silence_multi
        else
            start_node_silence
        fi
    else
        Logging "nodes can't be launch with silence mode in catkin_ws environment,please use silence mode in docker's autopilot environment"
    fi
fi

