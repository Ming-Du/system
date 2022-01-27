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

check_env() {
    #add environment to /root/.bashrc
    env_roshostname_root=$(grep "export\b[[:space:]]*ROS_HOSTNAME" /root/.bashrc | grep -v "^#")
    if [ -z "$env_roshostname_root" ]; then
        echo "export ROS_HOSTNAME=$ros_machine" >>/root/.bashrc
    fi
    env_rosmasteruri_root=$(grep "export\b[[:space:]]*ROS_MASTER_URI" /root/.bashrc | grep -v "^#")
    if [ -z "$env_rosmasteruri_root" ]; then
        echo "export ROS_MASTER_URI=http://$ros_master:11311" >>/root/.bashrc
    fi
    #add environment to /home/mogo/.bashrc
    env_roshostname_mogo=$(grep "export\b[[:space:]]*ROS_HOSTNAME" /home/mogo/.bashrc | grep -v "^#")
    if [ -z "$env_roshostname_mogo" ]; then
        echo "export ROS_HOSTNAME=$ros_machine" >>/home/mogo/.bashrc
    fi
    env_rosmasteruri_mogo=$(grep "export\b[[:space:]]*ROS_MASTER_URI" /home/mogo/.bashrc | grep -v "^#")
    if [ -z "$env_rosmasteruri_mogo" ]; then
        echo "export ROS_MASTER_URI=http://$ros_master:11311" >>/home/mogo/.bashrc
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

create_roslog_config_file() {
    local pkg_set
    if [ -f $ROSCONSOLE_CONFIG_FILE ]; then
        rm -f $ROSCONSOLE_CONFIG_FILE
    fi
    Logging "${#nodes_array[@]} nodes will be launched"
    for root_file in "${nodes_array[@]}"; do
        include_file=$(roslaunch --files $root_file)
        for child_file in $include_file; do
            if [ -z "$child_file" ]; then
                continue
            fi
            pkg_name=$(xmllint --xpath "//@pkg" $child_file | sed 's/\"//g')
            if [ -z "$pkg_name" ]; then
                continue
            fi
            for value in $pkg_name; do
                pkg=$(echo "$value" | awk -F= '{print $2}')
                if [ $(echo $pkg_set | grep -o "$pkg" | wc -l) -eq 0 ]; then
                    pkg_set="$pkg_set|$pkg"
                    add_config $pkg
                fi
            done
        done
    done
}

start_node() {
    while read node; do
        Logging "roslaunch $node"
        include_file=$(roslaunch --files $node)
        for child_file in $include_file; do
            if [ -z "$child_file" ]; then
                continue
            fi
            pkg_name=$(xmllint --xpath "//@pkg" $child_file | sed 's/\"//g')
            if [ -z "$pkg_name" ]; then
                continue
            fi
            for value in $pkg_name; do
                pkg=$(echo "$value" | awk -F= '{print $2}')
                if [ $(echo $pkg_set | grep -o "$pkg" | wc -l) -eq 0 ]; then
                    pkg_set="$pkg_set|$pkg"
                    add_config $pkg INFO >$ROSCONSOLE_CONFIG_FILE
                fi
            done
        done
        launch_file=$(echo $node | awk '{print $NF}' | awk -F/ '{print $NF}')
        if [ "$GuiServer" == "silence" ]; then
            roslaunch --wait $node >${ROS_LOG_DIR}/${launch_file}.log 2>${ROS_LOG_DIR}/${launch_file}.err &
        else
            $GuiTerminal --tab -e "bash -c 'sleep 3; $BASHRC && roslaunch --wait $node 2>${ROS_LOG_DIR}/${launch_file}.err 2>&1 | tee -i ${ROS_LOG_DIR}/${launch_file}.log';bash" $TitleOpt "${launch_file}" &
        fi
        sleep 1
    done <$ListFile
}

Logging() {
    datetime=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$datetime] $*"
    echo "[$datetime] $*" >>$LOGFILE
}
install_ros_log()
{
     src_so_path=`find  /autocar-code/install/  -name 'libroscpp.so' | head -n 1`
     dst_so_path=`find  /opt -name  'libroscpp.so' | head -n 1`
     conf_path=`find   /autocar-code/install/   -name 'ros_statics.conf' | head -n 1`
     dst_conf_path="/home/mogo/data/log/ros_statics.conf"
     mkdir -p /home/mogo/data/log/ROS_STAT/
     mkdir -p /home/mogo/data/log/ROS_STAT/EXPORT
     chmod 777 -R /home/mogo/data/log/
     \cp -rf $src_so_path  $dst_so_path	
     \cp -rf $conf_path    $dst_conf_path
}
# main
export ABS_PATH # autopilot.sh脚本的路径
ABS_PATH="$(cd "$(dirname $0)" && pwd)"
LOGFILE="/home/mogo/data/log/autopilot.log"

install_ros_log
# 自动驾驶自检
stat_file="/home/mogo/data/vehicle_monitor/check_system.txt"
while [ true ]; do
    # 运维自检状态
    if [ -f $stat_file ];then
        [[ $(head -1 $stat_file) -ne 0 ]] && Logging "system check failed" && continue
    fi
    bash $ABS_PATH/check.sh c >>$LOGFILE
    if [ $? -eq 0 ]; then
        break
    fi
    Logging "autopilot check failed"
    sleep 1
    continue
done

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
        Logging "systime synchronization at $systime"
        echo $systime >$ABS_PATH/launch_time
        break
    fi
    sleep 1
done
curtime=$(date +"%Y%m%d%H%M%S")
mv $LOGFILE "/home/mogo/data/log/autopilot-${curtime}.log"
LOGFILE="/home/mogo/data/log/autopilot-${curtime}.log"
Logging "path : $ABS_PATH"
if [ $# -eq 0 ]; then
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
export VehicleType=$1 # VehicleType    wey jinlv byd df ...
# RunMode    1:autopilot    0:catkin_ws
export RunMode         # 运行方式  0：在catkin_ws环境中运行的debug模式  1：在autopilot环境中运行的release模式
export GuiTerminal     # 使用的terminal程序的绝对路径，如/usr/bin/xfce4-terminal
export TitleOpt        # 指定terminal窗口标题的选项，xfce为'-T'，gnome为'-t'
export SETUP_ROS       # ros系统自带的setup.bash路径，一般位于/opt/ros/melodic/setup.bash
export SETUP_AUTOPILOT # 用户程序的setup.bash
export VEHICLE_PLATE
if [ -f /home/mogo/data/vehicle_monitor/vehicle_config.txt ];then
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
    Logging "RunMode is $RunMode"
fi
vehicletypes="wey df hq byd jinlv"
if [ $(echo $vehicletypes | grep -wc $VehicleType) -lt 1 ]; then
    Logging "error:不支持此车型。车型：$VehicleType"
    Usage
    exit 1
fi

if [ "$GuiServer" == "silence" -a $RunMode -eq 0 ]; then
    Logging "nodes can't be launch with silence mode in catkin_ws environment,please use silence mode in docker's autopilot environment"
    exit 1
fi
export ros_master="localhost"
export xavier_type="single"        #单xavier or 双xavier
export ros_machine="${ros_master}" #主机:rosmaster 从机:rosslave
# 判断是否为双Xavier
ethnet_ip=$(ifconfig eth0 | grep -Eo '([0-9]+[.]){3}[0-9]+' | grep -v "255")
[[ -z "$ethnet_ip" ]] && Logging "ip address is null" && exit 1

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
check_env
Logging "rosmachine:${ros_machine} rosmaster:${ros_master} xavier_type:${xavier_type}"

if [ "$GuiServer" = "x" ]; then
    GuiTerminal="/usr/bin/xfce4-terminal"
    TitleOpt="-T"
elif [ "$GuiServer" = "g" ]; then
    GuiTerminal="/usr/bin/gnome-terminal"
    TitleOpt="-t"
else
    GuiServer="silence"
    Logging "GuiServer is $GuiServer"
fi

export GLOG_logtostderr=1
export GLOG_colorlogtostderr=1
export LOG_DIR="/home/mogo/data/log"
# ros日志存储路径的环境变量
export ROS_LOG_DIR="${LOG_DIR}/$(date +"%Y%m%d_%H%M%S")"
export BAG_DIR="/home/mogo/data/bags"
# ros日志配置文件的环境变量
# export ROSCONSOLE_FORMAT='[${severity}] ${time} [${function}(${line})]:${message}'
export ROSCONSOLE_CONFIG_FILE="$ABS_PATH/../config/rosconsole.config"
Logging "ROSCONSOLE_CONFIG_FILE=${ROSCONSOLE_CONFIG_FILE}"
export ROS_HOSTNAME=${ros_machine}
export ROS_MASTER_URI=http://${ros_master}:11311
export launch_prefix="roslaunch --wait"
export LOG_ENV="export GLOG_logtostderr=1; export GLOG_colorlogtostderr=1; export ROS_LOG_DIR=${ROS_LOG_DIR}; export ROS_MASTER_URI=http://${ros_master}:11311; export ROS_HOSTNAME=${ros_machine}"
[[ ! -d $ROS_LOG_DIR ]] && mkdir -p $ROS_LOG_DIR
ln -snf $ROS_LOG_DIR ${LOG_DIR}/latest
Logging "ROS_LOG_DIR=$ROS_LOG_DIR"
[[ ! -d $BAG_DIR ]] && mkdir -p $BAG_DIR

core_pid=$(ps aux | grep -v grep | grep "roscore$" | awk '{print $2}')
if [ ! -z "$core_pid" ]; then
    rosnode kill -a
    kill $core_pid
fi

find ${LOG_DIR} -maxdepth 1 -mtime +3 -type d -exec rm -Rf {} \;
find ${LOG_DIR} -name "autopilot*.log" -mtime +1 -exec rm -Rf {} \;
find $BAG_DIR -maxdepth 1 -mtime +1 -type d -exec rm -Rf {} \;

export BASHRC="source ${SETUP_ROS} && source ${SETUP_AUTOPILOT}"
source $SETUP_ROS
source $SETUP_AUTOPILOT

# 配置更新
rosrun update_config update_config 2>&1 > $ROS_LOG_DIR/update_config.log

if [ "$ros_machine" == "rosmaster" ]; then
    roscore 2>&1 >$ROS_LOG_DIR/roscore.log &
    python3 /home/mogo/autopilot/share/config/keylog_parser/log_collect_client.py & 
else
    python3 /home/mogo/autopilot/share/config/keylog_parser/log_collect_server.py & 
    python3 /home/mogo/autopilot/share/config/keylog_parser/log_resolver.py &
fi
# create_roslog_config_file
start_node
