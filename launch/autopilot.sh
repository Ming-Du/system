#!/bin/bash

Usage() {
    echo "Usage:"
    echo -e "\t$(basename $0) <VehicleType> [Style] [Options]"
    echo
    echo -e "\t<wey|byd|jinlv|df|hq> [silence|x|g] [[-n|--start-node <node-name>]|[-k|--keep-alive]|[-h|--help]]"
    echo -e "\tVehicleType                    \t\twey:长城 byd:比亚迪 jinlv:小巴 df:东风 hq:红旗 "
    echo -e "\tStyle                          \t\tsilence:后台启动(默认) x:xfce4窗口启动 g:gnome窗口启动"
    echo -e "\tOptions:"
    echo -e "\t\t-n|--start-node <node-name>  \t启动单个节点\tnode-name 节点名,eg:telematics"
    echo -e "\t\t-k|--keep-alive              \t监控模式,指定此选项当某节点退出时会重新启动该节点"
    echo -e "\t\t-h|--help                    \t帮助"
    echo
    echo "eg:"
    echo -e "\t.================================================"
    echo -e "\t|$(basename $0) df \t非监控模式后台启动东风车的所有节点"
    echo -e "\t|================================================"
    echo -e "\t|$(basename $0) df x\t非监控模式xface4窗口启动东风车的所有节点(容器内)"
    echo -e "\t|================================================"
    echo -e "\t|$(basename $0) df g\t非监控模式gnome窗口启动东风车的所有节点(宿主机)"
    echo -e "\t|================================================"
    echo -e "\t|$(basename $0) jinlv -k"
    echo -e "\t|$(basename $0) jinlv --keep-alive \t监控模式后台启动小巴车的所有节点"
    echo -e "\t|================================================"
    echo -e "\t|$(basename $0) hq -n local_planning"
    echo -e "\t|$(basename $0) hq --start-node local_planning \t只后台启动红旗车local_planning节点(不会启动roscore,需要手动启动)"
    echo -e "\t|================================================"
}

MOGO_LOG() {
    local code=$1
    local msg=$2
    local append
    [[ -f $MOGO_MSG_CONFIG ]] && append=$(cat $MOGO_MSG_CONFIG | python -c "import json,sys; sys.stdout.write(json.dumps(json.load(sys.stdin).get('$code')));sys.stdout.write('\n');" 2>/dev/null | sed 's/[\{\}]//g')
    append=${append:-"\"level\":\"$([ "${code:0:1}" != "E" ] && echo error || echo info)\", \"code\":\"$code\""}
    echo "{\"timestamp\": {\"sec\": $(date +"%s"), \"nsec\": $(date +"%N" | sed 's/^0*//g')}, \"src\": \"$this\", $append, \"msg\": \"$msg\"}" >>$MOGOLOGFILE
}

set_bashrc() {
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

    add_alias="alias cdl='cd /home/mogo/data/log'"
    alias_log=$(grep "alias\b[[:space:]]*cdl" ~/.bashrc | grep -v "^#" | tail -1)
    c_alias_log=$(echo $alias_log | awk -F= '{print $2}')
    if [ -z "$c_alias_log" ]; then
        echo "$add_alias" >>~/.bashrc
    elif [ "$alias_log" != "'cd /home/mogo/data/log'" ]; then
        sed -i "s#^$alias_log#$add_alias#g" ~/.bashrc
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

        alias_log=$(grep "alias\b[[:space:]]*cdl" /home/mogo/.bashrc | grep -v "^#" | tail -1)
        c_alias_log=$(echo $alias_log | awk -F= '{print $2}')
        if [ -z "$c_alias_log" ]; then
            echo "$add_alias" >>/home/mogo/.bashrc
        elif [ "$alias_log" != "'cd /home/mogo/data/log'" ]; then
            sed -i "s#^$alias_log#$add_alias#g" /home/mogo/.bashrc
        fi
    fi
}
add_config() {
    # echo "package name:$1"
    local pkg_name=$1
    local pkg_log_dir=${ROS_LOG_DIR}/${pkg_name}
    [[ ! -d ${pkg_log_dir} ]] && mkdir -p ${pkg_log_dir}
    local level=${2:-ERROR}
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
}

get_all_launch_files() {
    local file_set
    if [[ ! -f $1 || $(sed '/^\s*$/d' $1 | wc -m) -eq 0 ]]; then
        LoggingERR "list file:$1 doesn't exist or it's empty" "EINIT_BOOT"
        return 1
    fi
    while read launch_file || [[ -n $launch_file ]]; do
        [[ -z "$launch_file" ]] && continue
        [[ $(echo $launch_file | awk '{print NF}') -eq 1 ]] && real_file=$launch_file || real_file=$(find $(roscd  ${launch_file% *} && pwd) -name ${launch_file#* })
        [[ ! -f $real_file ]] && LoggingERR "cannot locate $real_file" "EINIT_BOOT" && continue
        [[ -z "$(xmllint --xpath "//include/@file" $real_file 2>/dev/null)" ]] && include_files=$real_file || include_files=$(roslaunch --files $real_file 2>/dev/null)
        local should_start_list=""
        for child_file in $include_files; do
            [[ -z "$child_file" ]] && continue
            [[ $(echo $file_set | grep -w -c "$child_file:") -ne 0 ]] && continue
            type_name=$(xmllint --xpath "//node[@pkg!='rviz']/@type" $child_file 2>/dev/null | sed 's/\"//g')
            [[ -z "$type_name" ]] && continue
            should_start_list=$should_start_list:$child_file
            [[ -z "$(xmllint --xpath "//include/@file" $child_file 2>/dev/null)" ]] && continue
            for f in $(roslaunch --files $child_file); do
                [[ $(echo $file_set | grep -w -c "$f:") -ne 0 ]] && continue
                file_set="$f:$file_set"
                [[ "$f" != "$child_file" ]] && should_start_list=$(echo ${should_start_list} | sed "s#:*$f##g")
            done
        done
        for v in $(echo ${should_start_list//:/ });do
            map_restart_times[$v]=-1
            launch_files_array+=("$v")
        done
    done <$1
    return 0
}

start_onenode() {
    local real_launch_file="$1"
    local pkg_name
    pkg_name=$(xmllint --xpath "//@pkg" $real_launch_file 2>/dev/null | sed 's/\"//g')
    for value in $pkg_name; do
        pkg=${value/*=/}
        if [ $(echo $pkg_set | grep -o "$pkg" | wc -l) -eq 0 ]; then
            pkg_set="$pkg_set|$pkg"
            ROSCONSOLE_CONFIG_FILE="$ABS_PATH/../config/${pkg}_console.config"
            add_config $pkg INFO >$ROSCONSOLE_CONFIG_FILE
        fi
    done
    LoggingINFO "launching ${real_launch_file}..."
    launch_file=$(echo $real_launch_file | awk '{print $NF}' | awk -F/ '{print $NF}')
    if [ "$GuiServer" == "silence" ]; then
        roslaunch --wait $real_launch_file >>${ROS_LOG_DIR}/${launch_file}.log 2>>${ROS_LOG_DIR}/${launch_file}.err &
    else
        $GuiTerminal --tab -e "bash -c 'sleep 3; $BASHRC && roslaunch --wait $real_launch_file 2>${ROS_LOG_DIR}/${launch_file}.err 2>&1 | tee -i ${ROS_LOG_DIR}/${launch_file}.log';bash" $TitleOpt "${launch_file}" &
    fi
    map_restart_times[$real_launch_file]=$((map_restart_times[$real_launch_file] + 1))
}

start_node() {
    LoggingINFO "launching all..." "IMAP_START_TIME"
    for launch_file in ${launch_files_array[*]}; do
        start_onenode "$launch_file"
    done
}

keep_alive() {
    local restart=0 init=1
    # check node launch status
    while [ $opt_alive -eq 1 -a $exit_flag -ne 1 ]; do
        sleep 5
        core_stat=$(timeout 0.2 cat &>/dev/null </dev/tcp/$ros_master/11311) # check roscore
        if [ $? -ne 124 ]; then                                              #roscore exit
            LoggingERR "disconnected with roscore" "EMAP_NODE"
            restart=1
            # close child launch process
            [[ $(jobs -p | wc -l) -ne 0 ]] && jobs -p | xargs kill -2 >/dev/null 2>&1
            # restart roscore
            [[ "$ros_machine" == "$ros_master" ]] && start_core
            continue
        fi
        # nodes need to be restarted
        if [ $restart -eq 1 ]; then
            restart=0
            init=1
            LoggingINFO "roscore has been restarted,will start all local nodes..."
            start_node
            continue
        fi
        local node_stat=0
        for launch_file in ${launch_files_array[*]}; do
            nodes=$(roslaunch --nodes $launch_file | awk -F/ '{print $NF}') #当node模块定义name时有bug
            [[ -z "$nodes" ]] && continue
            proc_stat=0
            for t in $nodes; do
                # real_proc=$(echo $t | awk -F= '{print $2}')
                [[ "$t" =~ "rviz" ]] && continue
                [[ "$t" =~ "update_map" ]] && continue
                if [ $(ps -ef | grep "__name:=$t" | grep -v grep | wc -l) -eq 0 ]; then
                    proc_stat=1
                    ((node_stat++))
                    # runtime error
                    if [ ${map_restart_times[$launch_file]} -ge 1 -a ${map_restart_times[$launch_file]} -le 5 ]; then
                        LoggingERR "$t died,will restart it [${map_restart_times[$launch_file]}/5]" "EMAP_NODE"
                        LoggingINFO "will restart $t in $launch_file [${map_restart_times[$launch_file]}/5]"
                        start_onenode "$launch_file"
                        break
                    # try to restart failed
                    elif [ ${map_restart_times[$launch_file]} -eq 6 ]; then
                        map_restart_times[$launch_file]=999
                        LoggingERR "restart $t failed 5 times,cancel to restart" "EMAP_NODE_DEAD"
                    # launch error
                    elif [ ${map_restart_times[$launch_file]} -eq 0 ]; then
                        LoggingERR "launch $t failed" "EINIT_BOOT"
                        # map_restart_times[$launch_file]=1 #bug:如果launch里面有多个node，则只打印一次日志
                    fi
                else
                    if [ ${map_restart_times[$launch_file]} -gt 1 -a ${map_restart_times[$launch_file]} -lt 5 ]; then
                        LoggingINFO "$t restart succeed" "IBOOT_LOCAL_NODES_STATUS"
                    elif [ ${map_restart_times[$launch_file]} -eq 0 ]; then
                        LoggingINFO "launch $t succeed" "IBOOT_LOCAL_NODES_STATUS"
                        # map_restart_times[$launch_file]=1 #bug:如果launch里面有多个node，则只打印一次日志
                    fi
                    #pr
                    pid=$(ps -ef | grep "__name:=$t" | grep -v grep | awk '{print $2}')
                    [[ -z "$pid" ]] && continue
                    priority=$(top -b -n 1 -p $pid | grep $pid | awk '{print $(NF-9)}')
                    [[ "$priority" == "rt" ]] && continue
                    case "$t" in
                    "DongFeng_E70_can_adapter" | "jinlv_can_adapter" | "hongqih9_can_adapter") (($priority >= 0)) && chrt -p -r 99 $pid ;;
                    "controller") (($priority >= 0)) && chrt -p -r 99 $pid ;;
                    "localization" | "drivers_gnss" | "drivers_gnss_zy") (($priority >= 0)) && chrt -p -r 99 $pid ;;
                    "local_planning") (($priority >= 0)) && chrt -p -r 99 $pid ;;
                    "hadmap_server" | "hadmap_engine_node") (($priority >= 0)) && chrt -p -r 80 $pid ;;
                    "perception_fusion2" | "perception_fusion") (($priority >= 0)) && chrt -p -r 79 $pid ;;
                    "rs_perception_node" | "trt_yolov5") (($priority >= 0)) && chrt -p -r 69 $pid ;;
                    "drivers_camera_sensing60" | "drivers_camera_sensing30" | "drivers_camera_sensing120" | "drivers_robosense_node")
                        (($priority >= 0)) && chrt -p -r 59 $pid ;;
                    *) ;;
                    esac
                fi
            done
            [[ $proc_stat -eq 0 ]] && map_restart_times[$launch_file]=1
            [[ $proc_stat -ne 0 && ${map_restart_times[$launch_file]} -eq 0 ]] && map_restart_times[$launch_file]=1
        done
        if [ $init -eq 1 ]; then
            init=0
            if [[ $node_stat -ne 0 ]]; then
                LoggingERR "partial nodes launch failed,some function maybe abnormal." "EINIT_BOOT"
            else
                LoggingINFO "All nodes in ${ros_machine} launched successfully.${ros_mashine} init finished." "IBOOT_MAP_STARTED"
            fi
        fi
    done
}

LoggingINFO() {
    datetime=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "\033[32m[ INFO] [$datetime]$model:$1\033[0m"
    flock -x 6
    [[ -n "$LOGFILE" ]] && echo "[ INFO] [$datetime]$model:$1" >>$LOGFILE
    [[ -n "$2" ]] && MOGO_LOG "$2" "$1"
    flock -u 6
}

LoggingERR() {
    datetime=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "\033[31m[ERROR] [$datetime]$model:$1\033[0m" >/dev/stderr
    flock -x 6
    [[ -n "$LOGFILE" ]] && echo "[ERROR] [$datetime]$model:$1" >>$LOGFILE
    flock -u 6
    flock -x 7
    [[ -n "$ERRFILE" ]] && echo "[ERROR] [$datetime]$model:$1" >>$ERRFILE
    [[ -n "$2" ]] && MOGO_LOG "$2" "$1"
    flock -u 7
}

get_xavier_type() {
    # check xavier type
    ethnet_ip=$(ifconfig | grep -v "inet6" | grep -Eo '192[.]168([.][0-9]+){2}' | grep -v "255")
    if [ -z "$ethnet_ip" ]; then
        LoggingERR "ip address is null" "EHW_NET"
        exit 1
    fi
    ros_machine=$(grep -Eo "^[^#]*$ethnet_ip[[:space:]]*ros[^#]*" /etc/hosts | uniq | head -1 | awk '{print $2}')
    rosmachine=${ros_machine:="localhost"}
    [[ ${rosmachine} == "localhost" ]] && ros_master="${rosmachine}" || ros_master="rosmaster"
    ros_hosts=$(grep -Eo "^[^#]*ros[^#]*" /etc/hosts | uniq | wc -l)
    return $((ros_hosts > 2 ? 3 : ((ros_hosts > 1 ? 2 : 1))))
}

get_launch_list() {
    get_xavier_type
    x_t=$?
    if [ ! -z "$opt_launch_file" ]; then
        echo "$opt_pkg $opt_launch_file" | sed 's/^\s*//g' >/tmp/tmp.list
        list_file="/tmp/tmp.list"
        return
    fi
    case $x_t in
    1) list_file=${ABS_PATH}/all.list ;;
    2) list_file=${ABS_PATH}/${ros_machine}.list ;;
    3) [[ ${ros_machine} == "rosmaster" ]] && list_file=${ABS_PATH}/rosmaster-102.list || list_file=${ABS_PATH}/${ros_machine}.list ;;
    *) ;;
    esac
}

install_ros_log() {
    [[ ! -d /autocar-code/install ]] && return
    src_so_path=$(find /autocar-code/install/ -name 'libroscpp.so' | head -n 1)
    dst_so_path=$(find /opt -name 'libroscpp.so' | head -n 1)
    \cp -rf $src_so_path $dst_so_path
    src_so_path=$(find /autocar-code/install/ -name 'libxmlrpcpp.so' | head -n 1)
    dst_so_path=$(find /opt -name 'libxmlrpcpp.so' | head -n 1)
    \cp -rf $src_so_path $dst_so_path
    mkdir -p /home/mogo/data/log/ROS_STAT/
    mkdir -p /home/mogo/data/log/ROS_STAT/EXPORT/
    chmod 777 -R /home/mogo/data/log/
}

add_privilege_monitor_gnss() {
    [[ ! -d /autocar-code/install ]] && return
    #rm /home/mogo/data/log/location.txt -rf
    #rm /home/mogo/data/log/msg_info_log.txt -rf
    #rm /home/mogo/data/log/msg_error_log.txt -rf
    #rm /home/mogo/data/log/topic_hz_log.txt -rf
    rm  -rf  /home/mogo/data/log/filebeat_upload/*
    chmod -R 777 /autocar-code/install/share/monitor_gnss >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/share/monitor_collect >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/share/monitor_process >/dev/null 2>&1
}

start_core() {
    [[ -n "$opt_onenode" ]] && return
    roscore 2>&1 >$ROS_LOG_DIR/roscore.log &
    roscore_pid=$!
    chrt -p -r 99 $roscore_pid
}
kill_ros() {
    [[ -n "$opt_onenode" || -n "$opt_launch_file" ]] && return
    core_pid=$(ps aux | grep -v grep | grep -w "rosmaster --core" | awk '{print $2}')
    [[ ! -z "$core_pid" ]] && kill -2 $core_pid
}
wait_core() {
    LoggingINFO "waiting roscore in ${ros_master:="localhost"}..."
    local ret=0
    while [ $ret -ne 124 -a $exit_flag -eq 0 ]; do
        timeout 1 cat &>/dev/null </dev/tcp/${ros_master}/11311
        ret=$?
    done
}
_exit() {
    LoggingINFO "receive SIGINT/SIGTERM signal or process proactively quit" "IBOOT_LOCAL_NODES_STATUS"
    [[ $exit_flag == 1 ]] && jobs -p | xargs kill -15 >/dev/null 2>&1
    exit 6
}
# main
trap 'killall mogodoctor.py 2>/dev/null;killall update_config 2>/dev/null;exit_flag=1;_exit' INT TERM
export ABS_PATH # autopilot.sh脚本的路径
ABS_PATH="$(cd "$(dirname $0)" && pwd)"

declare -A -g map_restart_times=()
declare -g launch_files_array=()
declare -g opt_onenode opt_alive=1 opt_pkg opt_launch_file
declare -g LOG_DIR="/home/mogo/data/log"
declare -g BAG_DIR="/home/mogo/data/bags"
declare -g -r MOGO_MSG_CONFIG="$ABS_PATH/config/mogo_report_msg.json"
declare -g -r MOGO_LOG_DIR="$LOG_DIR/msg_log"
declare -g -r MOGOLOGFILE="$MOGO_LOG_DIR/autopilot_report.json"
declare -g -r LOGFILE="/home/mogo/data/log/autopilot.log" #
declare -g -r ERRFILE="/home/mogo/data/log/autopilot.err" #
declare -g exit_flag=0 list_file roscore_pid ros_master ros_machine

exec 6>>$LOGFILE
exec 7>>$ERRFILE
exec 8>>/home/mogo/data/launch_time
self_pid=$$
this=${ABS_PATH}/$(basename $0)
args="$@"

param=$(getopt -a -o f:n:P:N:h --long list-file:,start-node:,pkg:,launch-file:,no-keep-alive,help -n 'autopilot.sh' -- "$@")
eval set -- "$param"
while true; do
    case "$1" in
    -h | --help)
        Usage
        shift
        exit 0
        ;;
    --launch-file)
        opt_launch_file=$2
        shift 2
        ;;
    -n | --start-node)
        opt_onenode=$2
        shift 2
        ;;
    --no-keep-alive)
        opt_alive=0
        shift 1
        ;;
    --pkg)
        opt_pkg=$2
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
#参数合法性判断
[[ -z "$opt_launch_file" && ! -z "$opt_pkg" ]] && LoggingERR "'--pkg' must be used with '--launch-file' together" && exit 1
[[ ! -z "$opt_launch_file" && ! -z "$opt_onenode" ]] && LoggingERR "'--launch-file' cannot use with '--start-node'" && exit 1

# GuiServer:silence -- 后台启动 xfce4 -- docker中启动 终端使用xfce4-terminal gnome -- 宿主机中启动 终端使用gnome-terminal
export GuiServer=${2:-silence}
export VehicleType=$1  # VehicleType    wey jinlv byd df ...
export GuiTerminal     # 使用的terminal程序的绝对路径，如/usr/bin/xfce4-terminal
export TitleOpt        # 指定terminal窗口标题的选项，xfce为'-T'，gnome为'-t'
export SETUP_ROS       # ros系统自带的setup.bash路径，一般位于/opt/ros/melodic/setup.bash
export SETUP_AUTOPILOT # 用户程序的setup.bash
export VEHICLE_PLATE
[[ ! -d $LOG_DIR ]] && mkdir -p $LOG_DIR
[[ ! -d $BAG_DIR ]] && mkdir -p $BAG_DIR && chown -R mogo:mogo $BAG_DIR
[[ ! -d $MOGO_LOG_DIR ]] && mkdir -p $MOGO_LOG_DIR

if [ -f /home/mogo/data/vehicle_monitor/vehicle_config.txt ]; then
    VEHICLE_PLATE=$(grep plate /home/mogo/data/vehicle_monitor/vehicle_config.txt | awk -F: '{print $2}' | sed -e 's/ //g' -e 's/\"//g')
fi
SETUP_ROS="/opt/ros/melodic/setup.bash"
if [ $(echo $ABS_PATH | grep -w "/home/mogo/autopilot" | wc -l) -eq 0 ]; then
    SETUP_AUTOPILOT="$ABS_PATH/../../../devel/setup.bash"
else
    SETUP_AUTOPILOT="$ABS_PATH/../../setup.bash"
fi
source $SETUP_ROS
source $SETUP_AUTOPILOT
if [ "$GuiServer" = "x" ]; then
    GuiTerminal="/usr/bin/xfce4-terminal"
    TitleOpt="-T"
elif [ "$GuiServer" = "g" ]; then
    GuiTerminal="/usr/bin/gnome-terminal"
    TitleOpt="-t"
fi
#check system time
declare last_launch_time
if [ -f $ABS_PATH/launch_time ]; then
    last_launch_time=$(cat $ABS_PATH/launch_time)
fi
last_launch_time=${last_launch_time:-"20211222211202"}
while [ true ]; do
    systime=$(date +"%Y%m%d%H%M%S")
    if [ $systime -gt $last_launch_time ]; then
        # check if mogo_msg config file exist
        [ ! -f $MOGO_MSG_CONFIG ] && LoggingERR "cannot get mogo_msg_config,report could be incompletion" "EINIT_BOOT"
        [[ ! -z "$opt_onenode" ]] && LoggingINFO "systime synchronization at $systime" "IINIT_TIME_SYNC"
        last_launch_time=$(date +"%F %T")
        echo $systime >$ABS_PATH/launch_time
        break
    fi
    sleep 1
done
clear_time=$(date -d "2 days ago" +"%Y%m%d%H%M%S")
flock -x 6
row=$(awk -F"\] \[|\]:" 'BEGIN{last=0};{gsub("(-|:| )","",$2);if($2<"'$clear_time'"){last=NR}else{exit}};END{print last}' $LOGFILE)
if [ $row -gt 0 ]; then
    sed -i "1,${row}d" $LOGFILE
fi
flock -u 6
flock -x 7
row=$(awk -F"\] \[|\]:" 'BEGIN{last=0};{gsub("(-|:| )","",$2);if($2<"'$clear_time'"){last=NR}else{exit}};END{print last}' $ERRFILE)
if [ $row -gt 0 ]; then
    sed -i "1,${row}d" $ERRFILE
fi
flock -u 7
LoggingINFO "systime synchronization at $(date +"%F %T")"

# ros日志存储路径的环境变量
export ROS_LOG_DIR="${LOG_DIR}/$(date +"%Y%m%d")"
flock -x 8
if [[ ! -d $ROS_LOG_DIR ]]; then
    find ${LOG_DIR} -maxdepth 1 -mtime +3 -type d -exec rm -Rf {} \;
    find $BAG_DIR -maxdepth 1 -mtime +1 -type d -exec rm -Rf {} \;
    mkdir -p $ROS_LOG_DIR
    ln -snf $ROS_LOG_DIR ${LOG_DIR}/latest
fi
flock -u 8
LoggingINFO "ROS_LOG_DIR=$ROS_LOG_DIR"

get_launch_list
if [ -n "$opt_launch_file" ]; then
    declare -g -r model=" [${opt_pkg:-"$opt_launch_file"}]"
else
    declare -g -r model=" [MAP]"
    pids=$(ps -ef | grep -w "autopilot\.sh" | grep -v grep | awk '!($3 in arr) && $2 != "'$self_pid'" && $3 != "'$self_pid'" {arr[$2]=$2};END{for(idx in arr){print arr[idx]}}')
    for pid in $pids; do [[ "$pid" != "$self_pid" ]] && LoggingINFO "clean exist $(basename $0)[$pid]" && kill -2 $pid; done
    # 自动驾驶自检
    stat_file="/home/mogo/data/vehicle_monitor/check_system.txt"
    while [ true ]; do
        # 运维自检状态
        sleep 1
        [[ -f $stat_file && $(head -1 $stat_file) -ne 0 ]] && LoggingERR "system check failed" && continue
        break
    done
    python $ABS_PATH/mogodoctor.py c >>$LOGFILE 2>>$ERRFILE
    install_ros_log
    add_privilege_monitor_gnss
    kill_ros
    [[ "$ros_machine" == "$ros_master" ]] && start_core
fi

vehicletypes="wey df hq byd jinlv kaiwo"
if [[ -z "$opt_launch_file" && (-z "$VehicleType" || $(echo $vehicletypes | grep -wc $VehicleType) -lt 1) ]]; then
    LoggingERR "vehicle type undefined" "EVHC_TYPE_UNDEFINED"
    Usage
    exit 1
fi
set_bashrc
LoggingINFO "cwd:$ABS_PATH    command:$0 $args"
LoggingINFO "rosmachine:${ros_machine} rosmaster:${ros_master}"
LoggingINFO "start list file:$list_file"

export ROSCONSOLE_CONFIG_FILE
export ROS_HOSTNAME=${ros_machine}
export ROS_MASTER_URI=http://${ros_master}:11311
export OMP_NUM_THREADS=1
export BASHRC="source ${SETUP_ROS} && source ${SETUP_AUTOPILOT}"
export ROS_ENV="export ROS_LOG_DIR=${ROS_LOG_DIR}; export ROS_MASTER_URI=http://${ros_master}:11311; export ROS_HOSTNAME=${ros_machine}"

ln -s /home/mogo/data/vehicle_monitor/vehicle /home/mogo/autopilot/share/config/vehicle

# start to launch
get_all_launch_files $list_file #获取所有需要启动的launch文件
wait_core
# 配置更新
timeout 300 roslaunch --wait update_config update_config.launch >$ROS_LOG_DIR/update_config.launch.log 2>$ROS_LOG_DIR/update_config.launch.err

# launch gnss

# launch telematics
ret=$?
if [ ! -z "$ret" ]; then
    if [ $ret -eq 124 ]; then LoggingERR "update config timeout" "EMAP_NODE";
    elif [ $ret -eq 0 ]; then LoggingINFO "update config finished" "IBOOT_CONFIG_UPDATE"; fi
else
    LoggingERR "didn't execute update_config opearation" "EMAP_NODE"
fi
start_node
[[ $opt_alive -ne 0 ]] && keep_alive && LoggingINFO "keep alive is runing..."
