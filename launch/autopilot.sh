#!/bin/bash

Usage() {
    echo "Usage:"
    echo "$(basename $0) <wey|byd|jinlv|df|hq> [silence|x|g]"
    echo "Options:"
    echo "wey        --长城车"
    echo "byd        --byd车"
    echo "jinlv      --小巴车"
    echo "df         --东风车"
    echo "hq         --红旗车"
    echo "silence    --后台启动[默认值]"
    echo "x          --xfce4窗口启动"
    echo "g          --gnome窗口启动"
}
kill_ros() {
    core_pid=$(ps aux | grep -v grep | grep -w "rosmaster --core" | awk '{print $2}')
    if [ ! -z "$core_pid" ]; then
        rosnode kill -a
        kill $core_pid
    fi
}
check_env() {
    HOSTNAME="export ROS_HOSTNAME=$ros_machine"
    MASTER_URI="export ROS_MASTER_URI=http://$ros_master:11311"
    #add environment to /root/.bashrc
    env_roshostname_user=$(grep "export\b[[:space:]]*ROS_HOSTNAME" ~/.bashrc | grep -v "^#" | tail -1)
    bashrc_hostname=$(echo $env_roshostname_user | awk -F= '{print $2}')
    if [ -z "$bashrc_hostname" ]; then
        echo "$HOSTNAME" >>~/.bashrc
    elif [ "$bashrc_hostname" != "$ros_machine" ]; then
        sed -i "s/$env_roshostname_user/$HOSTNAME/g" ~/.bashrc
    fi
    env_rosmasteruri_user=$(grep "export\b[[:space:]]*ROS_MASTER_URI" ~/.bashrc | grep -v "^#" | tail -1)
    bashrc_masteruri=$(echo $env_rosmasteruri_user | awk -F= '{print $2}')
    if [ -z "$bashrc_masteruri" ]; then
        echo "$MASTER_URI" >>~/.bashrc
    elif [ "$bashrc_masteruri" != "http://$ros_master:11311" ]; then
        sed -i "s#^$env_rosmasteruri_user#$MASTER_URI#g" ~/.bashrc
    fi
    #add environment to /home/mogo/.bashrc
    if [ "$HOME" == "/root" ]; then
        env_roshostname_mogo=$(grep "export\b[[:space:]]*ROS_HOSTNAME" /home/mogo/.bashrc | grep -v "^#" | tail -1)
        bashrc_hostname_mogo=$(echo $env_roshostname_mogo | awk -F= '{print $2}')
        if [ -z "$bashrc_hostname_mogo" ]; then
            echo "$HOSTNAME" >>/home/mogo/.bashrc
        elif [ "$bashrc_hostname_mogo" != "$ros_machine" ]; then
            sed -i "s/$env_roshostname_mogo/$HOSTNAME/g" /home/mogo/.bashrc
        fi
        env_rosmasteruri_mogo=$(grep "export\b[[:space:]]*ROS_MASTER_URI" /home/mogo/.bashrc | grep -v "^#" | tail -1)
        bashrc_masteruri_mogo=$(echo $env_rosmasteruri_mogo | awk -F= '{print $2}')
        if [ -z "$bashrc_masteruri_mogo" ]; then
            echo "$MASTER_URI" >>/home/mogo/.bashrc
        elif [ "$bashrc_masteruri_mogo" != "http://$ros_master:11311" ]; then
            sed -i "s#^$env_rosmasteruri_mogo#$MASTER_URI#g" /home/mogo/.bashrc
        fi
    fi
}
add_config() {
    # echo "package name:$1"
    local pkg_name=$1
    local pkg_log_dir=${ROS_LOG_DIR}/${pkg_name}
    [[ ! -d ${pkg_log_dir} ]] && mkdir -p ${pkg_log_dir}
    local level=$2
    if [ -z "$level" ]; then
        level="ERROR"
    fi
    local Aconsole=C${pkg_name}
    local InfoAppender=I_${pkg_name}
    local ErrorAppender=E_${pkg_name}
    local ErrorFile=${pkg_name}_ERROR.log
    local INFOFile=${pkg_name}_INFO.log
    echo "log4j.logger.ros.${pkg_name}=${level},${InfoAppender},${ErrorAppender}
log4j.appender.${InfoAppender}=org.apache.log4j.DailyRollingFileAppender
log4j.appender.${InfoAppender}.Threshold=INFO
log4j.appender.${InfoAppender}.ImmediateFlush=true
log4j.appender.${InfoAppender}.Append=true
log4j.appender.${InfoAppender}.File=${pkg_log_dir}/${INFOFile}
log4j.appender.${InfoAppender}.DatePattern='.'yyyy-MM-dd-HH
log4j.appender.${InfoAppender}.layout=org.apache.log4j.PatternLayout
log4j.appender.${InfoAppender}.layout.ConversionPattern=[%-5p] %d{yyyy-MM-dd HH:mm:ss.SSS} %l: %m %n

log4j.appender.${ErrorAppender}=org.apache.log4j.DailyRollingFileAppender
log4j.appender.${ErrorAppender}.Threshold=ERROR
log4j.appender.${ErrorAppender}.ImmediateFlush=true
log4j.appender.${ErrorAppender}.Append=true
log4j.appender.${ErrorAppender}.File=${pkg_log_dir}/${ErrorFile}
log4j.appender.${ErrorAppender}.DatePattern='.'yyyy-MM-dd-HH
log4j.appender.${ErrorAppender}.layout=org.apache.log4j.PatternLayout
log4j.appender.${ErrorAppender}.layout.ConversionPattern=[%-5p] %d{yyyy-MM-dd HH:mm:ss.SSS} LWP:%t(%r) %l: %m %n
"
    # log4j.appender.${Aconsole}=org.apache.log4j.ConsoleAppender
    # log4j.appender.${Aconsole}.Threshold=${level}
    # log4j.appender.${Aconsole}.ImmediateFlush=true
    # log4j.appender.${Aconsole}.Target=System.out
    # log4j.appender.${Aconsole}.layout=org.apache.log4j.PatternLayout
    # log4j.appender.${Aconsole}.layout.ConversionPattern=[%-5p] %d{yyyy-MM-dd HH:mm:ss.SSS} %l: %m %n
    # "
}

get_all_launch_files() {
    if [ -n "$startnode" ]; then
        launch_line=$(grep -w $startnode $ListFile)
        include_files=$(roslaunch --files $launch_line 2>/dev/null)
        if [ $? -ne 0 ]; then
            LoggingERR "cannot find $launch_line"
            exit 1
        fi
        for child_file in $include_files; do
            [[ -z "$child_file" ]] && continue
            pkg_name=$(xmllint --xpath "//@pkg" $child_file 2>/dev/null | sed 's/\"//g')
            [[ -z "$pkg_name" ]] && continue
            launch_files_array[$arr_idx]="$child_file"
            arr_idx=$((arr_idx + 1))
        done
        return
    fi
    while read launch_file || [[ -n $launch_file ]]; do
        include_files=$(roslaunch --files $launch_file 2>/dev/null)
        if [ $? -ne 0 ]; then
            LoggingERR "cannot find $launch_file"
            continue
        fi
        for child_file in $include_files; do
            [[ -z "$child_file" ]] && continue
            pkg_name=$(xmllint --xpath "//@pkg" $child_file 2>/dev/null | sed 's/\"//g')
            [[ -z "$pkg_name" ]] && continue
            launch_files_array[$arr_idx]="$child_file"
            arr_idx=$((arr_idx + 1))
        done
    done <$ListFile
}

start_onenode() {
    local real_launch_file="$1"
    local pkg_name

    pkg_name=$(xmllint --xpath "//@pkg" $real_launch_file 2>/dev/null | sed 's/\"//g')
    for value in $pkg_name; do
        pkg=$(echo "$value" | awk -F= '{print $2}')
        if [ $(echo $pkg_set | grep -o "$pkg" | wc -l) -eq 0 ]; then
            pkg_set="$pkg_set|$pkg"
            add_config $pkg INFO >$ROSCONSOLE_CONFIG_FILE
        fi
    done

    launch_file=$(echo $real_launch_file | awk '{print $NF}' | awk -F/ '{print $NF}')
    if [ "$GuiServer" == "silence" ]; then
        roslaunch --wait $real_launch_file >${ROS_LOG_DIR}/${launch_file}.log 2>${ROS_LOG_DIR}/${launch_file}.err &
    else
        $GuiTerminal --tab -e "bash -c 'sleep 3; $BASHRC && roslaunch --wait $real_launch_file 2>${ROS_LOG_DIR}/${launch_file}.err 2>&1 | tee -i ${ROS_LOG_DIR}/${launch_file}.log';bash" $TitleOpt "${launch_file}" &
    fi
}

start_node() {
    for launch_file in ${launch_files_array[*]}; do
        LoggingINFO "roslaunch $launch_file"
        start_onenode "$launch_file"
    done
}

keep_alive() {
    # check node launch status
    while [ true ]; do
        sleep 3
        for launch_file in ${launch_files_array[*]}; do
            pkg_type=$(xmllint --xpath "//node[@type]/@type" $launch_file 2>/dev/null | sed 's/\"//g')
            [[ -z "$pkg_type" ]] && continue
            for t in $pkg_type; do
                real_proc=$(echo $t | awk -F= '{print $2}')
                [[ "$real_proc" =~ "rviz" ]] && continue
                if [ $(ps -ef | grep -w $real_proc | grep -v grep | wc -l) -eq 0 ]; then
                    LoggingERR "$real_proc died,will restart..."
                    start_onenode "$launch_file"
                fi
            done
        done
    done
}

LoggingINFO() {
    datetime=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "\033[32m[ INFO] [$datetime] $*\033[0m"
    [[ -n "$LOGFILE" ]] && echo "[ INFO] [$datetime] $*" >>$LOGFILE
}

LoggingERR() {
    datetime=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "\033[31m[ERROR] [$datetime] $*\033[0m" >/dev/stderr
    [[ -n "$LOGFILE" ]] && echo "[ERROR] [$datetime] $*" >>$LOGFILE
    [[ -n "$ERRFILE" ]] && echo "[ERROR] [$datetime] $*" >>$ERRFILE
}

install_ros_log() {
    src_so_path=$(find /autocar-code/install/ -name 'libroscpp.so' | head -n 1)
    dst_so_path=$(find /opt -name 'libroscpp.so' | head -n 1)
    conf_path=$(find /autocar-code/install/ -name 'ros_statics.conf' | head -n 1)
    dst_conf_path="/home/mogo/data/log/ros_statics.conf"
    mkdir -p /home/mogo/data/log/ROS_STAT/
    mkdir -p /home/mogo/data/log/ROS_STAT/EXPORT/
    chmod 777 -R /home/mogo/data/log/
    \cp -rf $src_so_path $dst_so_path
    \cp -rf $conf_path $dst_conf_path
}

_exit() {
    LoggingINFO "receive quit signal"
    rosnode kill -a
    kill $roscore_pid
    exit 6
}
# main
trap '_exit' INT

param=$(getopt -o r --long start-node: -n 'autopilot.sh' -- "$@")
eval set -- "$param"
while true; do
    case "$1" in
    -r)
        echo "-r"
        shift
        ;;
    --start-node)
        startnode=$2
        shift 2
        ;;
    --)
        shift
        break
        ;;
    *)
        echo "error"
        exit 1
        ;;
    esac
done

declare launch_files_array
declare arr_idx=0
declare roscore_pid
declare LOGFILE
declare ERRFILE
self_pid=$$
if [ -z "$startnode" ]; then
    LOGFILE="/home/mogo/data/log/autopilot.log"
    ERRFILE="/home/mogo/data/log/autopilot.err"
    pids=$(ps -ef | grep -w "autopilot\.sh" | grep -v grep | awk '!($3 in arr) && $2 != "'$self_pid'" && $3 != "'$self_pid'" {arr[$2]=$2};END{for(idx in arr){print arr[idx]}}')
    for pid in $pids; do
        if [ "$pid" != "$self_pid" ]; then
            kill -2 $pid
            LoggingINFO "clean exist $(basename $0)[$pid]"
        fi
    done
fi

export ABS_PATH # autopilot.sh脚本的路径
ABS_PATH="$(cd "$(dirname $0)" && pwd)"

# GuiServer:
# silence -- 后台启动
# xfce4 -- docker中启动 终端使用xfce4-terminal
# gnome -- 宿主机中启动 终端使用gnome-terminal
export GuiServer=$2
export VehicleType=$1 # VehicleType    wey jinlv byd df ...
# RunMode    1:autopilot    0:catkin_ws
export RunMode         # 运行方式  0：在catkin_ws环境中运行的debug模式  1：在autopilot环境中运行的release模式
export GuiTerminal     # 使用的terminal程序的绝对路径，如/usr/bin/xfce4-terminal
export TitleOpt        # 指定terminal窗口标题的选项，xfce为'-T'，gnome为'-t'
export SETUP_ROS       # ros系统自带的setup.bash路径，一般位于/opt/ros/melodic/setup.bash
export SETUP_AUTOPILOT # 用户程序的setup.bash
export VEHICLE_PLATE
if [ -f /home/mogo/data/vehicle_monitor/vehicle_config.txt ]; then
    VEHICLE_PLATE=$(grep plate /home/mogo/data/vehicle_monitor/vehicle_config.txt | awk -F: '{print $2}' | sed -e 's/ //g' -e 's/\"//g')
fi
# autopilot:/home/mogo/autopilot/share/launch
# catkin_ws:/home/mogo/data/catkin_ws/src/system/launch
RunMode=$(echo $ABS_PATH | grep -w "/home/mogo/autopilot" | wc -l)
SETUP_ROS="/opt/ros/melodic/setup.bash"

if [ $RunMode -eq 0 ]; then
    SETUP_AUTOPILOT="$ABS_PATH/../../../devel/setup.bash"
elif [ $RunMode -eq 1 ]; then
    SETUP_AUTOPILOT="$ABS_PATH/../../setup.bash"
else
    LoggingINFO "RunMode is $RunMode"
fi
vehicletypes="wey df hq byd jinlv"
[[ -z "$VehicleType" ]] && LoggingERR "vehicle type undefined" && exit 1
if [ $(echo $vehicletypes | grep -wc $VehicleType) -lt 1 ]; then
    LoggingERR "error:不支持此车型。车型：$VehicleType"
    Usage
    exit 1
fi

if [ "$GuiServer" == "silence" -a $RunMode -eq 0 ]; then
    LoggingERR "nodes can't be launch with silence mode in catkin_ws environment,please use silence mode in docker's autopilot environment"
    exit 1
fi
export ros_master="localhost"
export xavier_type="single"        #单xavier or 双xavier
export ros_machine="${ros_master}" #主机:rosmaster 从机:rosslave
# 判断是否为双Xavier
ethnet_ip=$(ifconfig eth0 | grep -Eo '([0-9]+[.]){3}[0-9]+' | grep -v "255")
[[ -z "$ethnet_ip" ]] && LoggingERR "ip address is null" && exit 1

ros_machine=$(grep -E "$ethnet_ip.*ros.*" /etc/hosts | grep -v "^#" | uniq | head -1 | awk '{print $2}')
if [ -z "$ros_machine" ]; then
    xavier_type="single"
    ros_machine="titan-ubuntu1"
    ros_master=$ros_machine
    ListFile=${ABS_PATH}/all.list
else
    xavier_type="multi"
    if [ "$ros_machine" == "rosmaster" ]; then
        ros_master=$ros_machine
        slave_number=$(grep "rosslave" /etc/hosts | grep -v "^#" | uniq | wc -l)
        if [ $slave_number -gt 1 ]; then #6xaviers
            ListFile=${ABS_PATH}/rosmaster-102.list
        elif [ $slave_number -eq 1 ]; then           #single xavier
            ListFile=${ABS_PATH}/${ros_machine}.list #2xaviers
        else
            ListFile=${ABS_PATH}/all.list
        fi
    else
        ros_master="rosmaster"
        ListFile=${ABS_PATH}/${ros_machine}.list
    fi
fi
LoggingINFO "start list file:$ListFile"
check_env
LoggingINFO "rosmachine:${ros_machine} rosmaster:${ros_master} xavier_type:${xavier_type}"

if [ "$GuiServer" = "x" ]; then
    GuiTerminal="/usr/bin/xfce4-terminal"
    TitleOpt="-T"
elif [ "$GuiServer" = "g" ]; then
    GuiTerminal="/usr/bin/gnome-terminal"
    TitleOpt="-t"
else
    GuiServer="silence"
    LoggingINFO "GuiServer is $GuiServer"
fi

export GLOG_logtostderr=1
export GLOG_colorlogtostderr=1
export LOG_DIR="/home/mogo/data/log"
# ros日志存储路径的环境变量
export ROS_LOG_DIR
export BAG_DIR="/home/mogo/data/bags"
# ros日志配置文件的环境变量
# export ROSCONSOLE_FORMAT='[${severity}] ${time} [${function}(${line})]:${message}'
export ROSCONSOLE_CONFIG_FILE="$ABS_PATH/../config/rosconsole.config"
LoggingINFO "ROSCONSOLE_CONFIG_FILE=${ROSCONSOLE_CONFIG_FILE}"
export ROS_HOSTNAME=${ros_machine}
export ROS_MASTER_URI=http://${ros_master}:11311

export BASHRC="source ${SETUP_ROS} && source ${SETUP_AUTOPILOT}"
source $SETUP_ROS
source $SETUP_AUTOPILOT

get_all_launch_files

if [ -n "$startnode" ]; then
    ROS_LOG_DIR=$(readlink ${LOG_DIR}/latest)
    start_node
    sleep 1
    exit 0
fi

install_ros_log
# 自动驾驶自检
stat_file="/home/mogo/data/vehicle_monitor/check_system.txt"
while [ true ]; do
    # 运维自检状态
    if [ -f $stat_file ]; then
        [[ $(head -1 $stat_file) -ne 0 ]] && LoggingERR "system check failed" && continue
    fi
    bash $ABS_PATH/check.sh >>$LOGFILE 2>>$ERRFILE
    if [ $? -eq 0 ]; then
        break
    fi
    LoggingERR "autopilot check failed"
    sleep 1
    continue
done

#check system time
export last_launch_time
if [ -f $ABS_PATH/launch_time ]; then
    last_launch_time=$(cat $ABS_PATH/launch_time)
fi
if [ -z "$last_launch_time" ]; then
    last_launch_time="20211222211202" #随便初始的一个日期时间，不要在意细节
fi
while [ true ]; do
    systime=$(date +"%Y%m%d%H%M%S")
    if [ $systime -gt $last_launch_time ]; then
        LoggingINFO "systime synchronization at $systime"
        echo $systime >$ABS_PATH/launch_time
        break
    fi
    sleep 1
done
curtime=$(date +"%Y%m%d%H%M%S")
[[ -f $LOGFILE ]] && mv $LOGFILE "/home/mogo/data/log/autopilot-${curtime}.log"
[[ -f $ERRFILE ]] && mv $ERRFILE "/home/mogo/data/log/autopilot-${curtime}.err"
LOGFILE="/home/mogo/data/log/autopilot-${curtime}.log"
ERRFILE="/home/mogo/data/log/autopilot-${curtime}.err"

ROS_LOG_DIR="${LOG_DIR}/$(date +"%Y%m%d_%H%M%S")"
[[ ! -d $ROS_LOG_DIR ]] && mkdir -p $ROS_LOG_DIR
ln -snf $ROS_LOG_DIR ${LOG_DIR}/latest
LoggingINFO "ROS_LOG_DIR=$ROS_LOG_DIR"
[[ ! -d $BAG_DIR ]] && mkdir -p $BAG_DIR
export LOG_ENV="export GLOG_logtostderr=1; export GLOG_colorlogtostderr=1; export ROS_LOG_DIR=${ROS_LOG_DIR}; export ROS_MASTER_URI=http://${ros_master}:11311; export ROS_HOSTNAME=${ros_machine}"

LoggingINFO "path : $ABS_PATH"
if [ $# -eq 0 ]; then
    LoggingERR "error:请指定车型"
    Usage
    exit 0
fi
LoggingINFO "command : $0 $@"

find ${LOG_DIR} -maxdepth 1 -mtime +3 -type d -exec rm -Rf {} \;
find ${LOG_DIR} -name "autopilot*.log" -mtime +1 -exec rm -Rf {} \;
find $BAG_DIR -maxdepth 1 -mtime +1 -type d -exec rm -Rf {} \;

kill_ros

if [ "$ros_machine" == "$ros_master" ]; then
    roscore 2>&1 >$ROS_LOG_DIR/roscore.log &
    roscore_pid=$!
    if [ "$xavier_type" != "single" ]; then
        python3 /home/mogo/autopilot/share/config/keylog_parser/log_collect_client.py >/dev/null 2>&1 &
    fi
elif [ "$ros_machine" == "rosslave" -o "$ros_machine" == "rosslave-103" ]; then
    python3 /home/mogo/autopilot/share/config/keylog_parser/log_collect_server.py >/dev/null 2>&1 &
    python3 /home/mogo/autopilot/share/config/keylog_parser/log_resolver.py >/dev/null 2>&1 &
else
    python3 /home/mogo/autopilot/share/config/keylog_parser/log_collect_client.py >/dev/null 2>&1 &
fi

sleep 1
# 配置更新
timeout 120 roslaunch --wait update_config update_config.launch >$ROS_LOG_DIR/update_config.launch.log 2>$ROS_LOG_DIR/update_config.launch.err

# launch gnss

# launch telematics

if [ $? -eq 124 ]; then
    LoggingERR "update config timeout"
fi

start_node
keep_alive
