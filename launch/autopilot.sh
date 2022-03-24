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
    local append=$(cat $ABS_PATH/../config/mogo_report_msg.json | python -c "import json,sys; sys.stdout.write(json.dumps(json.load(sys.stdin).get('$code')));sys.stdout.write('\n');" | sed 's/[\{\}]//g')
    if [ -z "$append" ]; then
        if [ "$(echo $code | cut -c 1)" == 'E' ]; then
            level="error"
        elif [ "$(echo $code | cut -c 1)" == 'I' ]; then
            level="info"
        fi
        append="\"level\":\"$level\", \"code\":\"$code\""
    fi
    echo "{\"timestamp\": {\"sec\": $(date +"%s"), \"nsec\": $(date +"%N")}, \"src\": \"$this\", $append, \"msg\": \"$msg\"}" >>$MOGOLOGFILE
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

    add_alias="alias cdl='cd /home/mogo/data/log/latest'"
    alias_log=$(grep "alias\b[[:space:]]*cdl" ~/.bashrc | grep -v "^#" | tail -1)
    c_alias_log=$(echo $alias_log | awk -F= '{print $2}')
    if [ -z "$c_alias_log" ]; then
        echo "$add_alias" >>~/.bashrc
    elif [ "$alias_log" != "'cd /home/mogo/data/log/latest'" ]; then
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

        add_alias="alias cdl='cd /home/mogo/data/log/latest'"
        alias_log=$(grep "alias\b[[:space:]]*cdl" /home/mogo/.bashrc | grep -v "^#" | tail -1)
        c_alias_log=$(echo $alias_log | awk -F= '{print $2}')
        if [ -z "$c_alias_log" ]; then
            echo "$add_alias" >>/home/mogo/.bashrc
        elif [ "$alias_log" != "'cd /home/mogo/data/log/latest'" ]; then
            sed -i "s#^$alias_log#$add_alias#g" /home/mogo/.bashrc
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
    local file_set
    if [ ! -f $ListFile -o $(sed '/^\s*$/d' $ListFile | wc -m) -eq 0 ]; then
        MOGO_LOG "EINIT_BOOT" "$ListFile doesn't exist or it's empty"
        LoggingERR "$ListFile doesn't exist or it's empty"
        return
    fi
    if [ -n "$opt_onenode" ]; then
        launch_line=$(grep -w $opt_onenode $ListFile)
        if [ -z "$launch_line" ];then
            LoggingERR "cannot find \"$opt_onenode\" in $ListFile"
            exit 1
        fi
        include_files=$(roslaunch --files $launch_line 2>/dev/null)
        if [ $? -ne 0 ]; then
            LoggingERR "cannot find $launch_line"
            exit 1
        fi
        for child_file in $include_files; do
            [[ -z "$child_file" ]] && continue
            [[ $(echo $file_set | grep -w -c "$child_file:") -ne 0 ]] && continue
            type_name=$(xmllint --xpath "//node[@pkg!='rviz']/@type" $child_file 2>/dev/null | sed 's/\"//g')
            [[ -z "$type_name" ]] && continue
            map_restart_times[$child_file]=-1
            launch_files_array[$arr_idx]="$child_file"
            arr_idx=$((arr_idx + 1))
            for f in $(roslaunch --files $child_file);do
                [[ $(echo $file_set | grep -w -c "$f:") -ne 0 ]] && continue
                file_set="$f:$file_set"
            done
        done
        return
    fi
    while read launch_file || [[ -n $launch_file ]]; do
        [[ -z "$launch_file" ]] && continue
        include_files=$(roslaunch --files $launch_file 2>/dev/null)
        if [ $? -ne 0 ]; then
            LoggingERR "cannot find $launch_file"
            MOGO_LOG "EINIT_BOOT" "can not find $launch_file or the launch file is invalid"
            continue
        fi
        for child_file in $include_files; do
            [[ -z "$child_file" ]] && continue
            [[ $(echo $file_set | grep -w -c "$child_file:") -ne 0 ]] && continue
            type_name=$(xmllint --xpath "//node[@pkg!='rviz']/@type" $child_file 2>/dev/null | sed 's/\"//g')
            [[ -z "$type_name" ]] && continue
            map_restart_times[$child_file]=-1
            launch_files_array[$arr_idx]="$child_file"
            arr_idx=$((arr_idx + 1))
            # 可能存在的问题:当某launch文件中既包含节点又包含include时，如果roslaunch --files命令先打印子file,则还会出现启动多次的问题，待修复
            for f in $(roslaunch --files $child_file);do
                [[ $(echo $file_set | grep -w -c "$f:") -ne 0 ]] && continue
                file_set="$f:$file_set"
            done
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
            # ros日志配置文件的环境变量
            # export ROSCONSOLE_FORMAT='[${severity}] ${time} [${function}(${line})]:${message}'
            ROSCONSOLE_CONFIG_FILE="$ABS_PATH/../config/${pkg}_console.config"
            add_config $pkg INFO >$ROSCONSOLE_CONFIG_FILE
        fi
    done

    launch_file=$(echo $real_launch_file | awk '{print $NF}' | awk -F/ '{print $NF}')
    if [ "$GuiServer" == "silence" ]; then
        roslaunch --wait $real_launch_file >${ROS_LOG_DIR}/${launch_file}.log 2>${ROS_LOG_DIR}/${launch_file}.err &
    else
        $GuiTerminal --tab -e "bash -c 'sleep 3; $BASHRC && roslaunch --wait $real_launch_file 2>${ROS_LOG_DIR}/${launch_file}.err 2>&1 | tee -i ${ROS_LOG_DIR}/${launch_file}.log';bash" $TitleOpt "${launch_file}" &
    fi
    map_restart_times[$real_launch_file]=$((map_restart_times[$real_launch_file] + 1))
}

start_node() {
    for launch_file in ${launch_files_array[*]}; do
        LoggingINFO "roslaunch $launch_file"
        start_onenode "$launch_file"
        map_restart_times[$launch_file]=-1
    done
}

keep_alive() {
    local restart=0
    # check node launch status
    while [ true ]; do
        sleep 5
        core_stat=$(timeout 1 cat </dev/tcp/$ros_master/11311) # check roscore
        if [ $? -ne 124 ]; then                                #roscore exit
            MOGO_LOG "EMAP_NODE" "disconnected with roscore"
            LoggingERR "disconnected with roscore"
            restart=1
            # close child launch process
            if [ $(jobs -p | wc -l) -ne 0 ]; then
                jobs -p | xargs kill -2 >/dev/null 2>&1
            fi
            # restart roscore
            [[ "$ros_machine" == "$ros_master" ]] && start_core
            continue
        fi
        # nodes need to be restarted
        if [ $restart -eq 1 ]; then
            restart=0
            LoggingINFO "roscore has been restarted,will start all local nodes..."
            start_node
            continue
        fi

        for launch_file in ${launch_files_array[*]}; do
            # pkg_type=$(xmllint --xpath "//node[@type]/@type" $launch_file 2>/dev/null | sed 's/\"//g')
            nodes=$(roslaunch --nodes $launch_file | awk -F/ '{print $NF}')
            [[ -z "$nodes" ]] && continue
            proc_stat=0
            for t in $nodes; do
                # real_proc=$(echo $t | awk -F= '{print $2}')
                [[ "$t" =~ "rviz" ]] && continue
                [[ "$t" =~ "update_map" ]] && continue
                if [ $(ps -ef | grep "__name:=$t" | grep -v grep | wc -l) -eq 0 ]; then
                    proc_stat=1
                    # runtime error
                    if [ ${map_restart_times[$launch_file]} -ge 1 -a ${map_restart_times[$launch_file]} -le 5 ]; then
                        LoggingERR "$t died,will restart it [${map_restart_times[$launch_file]}/5]"
                        MOGO_LOG "EMAP_NODE" "$t died,will restart it [${map_restart_times[$launch_file]}/5]"
                        LoggingINFO "will restart $t in $launch_file [${map_restart_times[$launch_file]}/5]"
                        start_onenode "$launch_file"
                        break
                    # try to restart failed
                    elif [ ${map_restart_times[$launch_file]} -eq 6 ]; then
                        map_restart_times[$launch_file]=999
                        MOGO_LOG "EMAP_NODE_DEAD" "restart $t failed 5 times,cancel to restart"
                        LoggingERR "restart $t failed 5 times,cancel to restart"
                    # launch error
                    elif [ ${map_restart_times[$launch_file]} -eq 0 ]; then
                        MOGO_LOG "EINIT_BOOT" "launch $t failed"
                        LoggingERR "launch $t failed"
                        # map_restart_times[$launch_file]=1 #bug:如果launch里面有多个node，则只打印一次日志
                    fi
                else
                    if [ ${map_restart_times[$launch_file]} -gt 1 -a ${map_restart_times[$launch_file]} -lt 5 ]; then
                        MOGO_LOG "IBOOT_LOCAL_NODES_STATUS" "restart $t succeed"
                        LoggingINFO "$t restart succeed"
                    elif [ ${map_restart_times[$launch_file]} -eq 0 ]; then
                        MOGO_LOG "IBOOT_LOCAL_NODES_STATUS" "launch $t succeed"
                        LoggingINFO "launch $t succeed" 
                        # map_restart_times[$launch_file]=1 #bug:如果launch里面有多个node，则只打印一次日志
                    fi
                    #pr
                    pid=$(ps -ef | grep "__name:=$t" | grep -v grep | awk '{print $2}')
                    if [ -z "$pid" ]; then
                        continue
                    fi
                    priority=$(top -b -n 1 -p $pid | grep $pid | awk '{print $(NF-9)}')
                    if [ "$priority" == "rt" ]; then
                        continue
                    fi

                    case "$t" in
                    "DongFeng_E70_can_adapter" | "jinlv_can_adapter" | "hongqih9_can_adapter")
                        if [ $priority -gt 0 ]; then
                            chrt -p -r 99 $pid
                        fi
                        ;;
                    "controller")
                        if [ $priority -gt 0 ]; then
                            chrt -p -r 99 $pid
                        fi
                        ;;

                    "localization" | "drivers_gnss" | "drivers_gnss_zy")
                        if [ $priority -gt 0 ]; then
                            chrt -p -r 99 $pid
                        fi
                        ;;
                    "local_planning")
                        if [ $priority -gt 0 ]; then
                            chrt -p -r 99 $pid
                        fi
                        ;;
                    "hadmap_server" | "hadmap_engine_node")
                        if [ $priority -gt 0 ]; then
                            chrt -p -r 80 $pid
                        fi
                        ;;
                    "perception_fusion2" | "perception_fusion")
                        if [ $priority -gt 0 ]; then
                            chrt -p -r 79 $pid
                        fi
                        ;;
                    "rs_perception_node" | "trt_yolov5")
                        if [ $priority -gt 0 ]; then
                            chrt -p -r 69 $pid
                        fi
                        ;;
                    "drivers_camera_sensing60" | "drivers_camera_sensing30" | "drivers_camera_sensing120" | "drivers_robosense_node")
                        if [ $priority -gt 0 ]; then
                            chrt -p -r 59 $pid
                        fi
                        ;;
                    *) ;;

                    esac
                fi
            done
            [[ $proc_stat -eq 0 ]] && map_restart_times[$launch_file]=1
            [[ $proc_stat -ne 0 && ${map_restart_times[$launch_file]} -eq 0 ]] && map_restart_times[$launch_file]=1
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
    [[ ! -d /autocar-code/install ]] && return
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

add_privilege_monitor_gnss() {
    [[ ! -d /autocar-code/install ]] && return
    rm /home/mogo/data/log/location.txt -rf
    rm /home/mogo/data/log/msg_info_log.txt -rf
    rm /home/mogo/data/log/msg_error_log.txt -rf
    rm /home/mogo/data/log/topic_hz_log.txt -rf
    chmod -R 777 /autocar-code/install/share/monitor_gnss >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/share/monitor_collect >/dev/null 2>&1
}

start_core() {
    [[ -n "$opt_onenode" ]] && return
    roscore 2>&1 >$ROS_LOG_DIR/roscore.log &
    roscore_pid=$!
    chrt -p -r 99 $roscore_pid
}
kill_ros() {
    [[ -n "$opt_onenode" ]] && return
    core_pid=$(ps aux | grep -v grep | grep -w "rosmaster --core" | awk '{print $2}')
    if [ ! -z "$core_pid" ]; then
        rosnode kill -a
        kill $core_pid
    fi
}

_exit() {
    MOGO_LOG "IBOOT_LOCAL_NODES_STATUS" "receive SIGINT/SIGTERM signal,will shutdown"
    LoggingINFO "receive quit signal"
    [[ ! -z "$roscore_pid" ]] && rosnode kill -a && kill $roscore_pid
    exit 6
}
# main
trap '_exit;killall mogodoctor.py' INT TERM

export ABS_PATH # autopilot.sh脚本的路径
ABS_PATH="$(cd "$(dirname $0)" && pwd)"

declare -A -g map_restart_times=()
declare -g opt_onenode
declare -g opt_alive=1
declare -g launch_files_array
declare -g arr_idx=0
declare -g roscore_pid
declare -g LOGFILE
declare -g ERRFILE
declare -g LOG_DIR="/home/mogo/data/log"
declare -g MOGO_MSG_CONFIG="$ABS_PATH/../config/mogo_report_msg.json"
declare -g MOGO_LOG_DIR="$LOG_DIR/msg_log"
declare -g MOGOLOGFILE="$MOGO_LOG_DIR/autopilot_report.json"
self_pid=$$
this=${ABS_PATH}/$(basename $0)

param=$(getopt -a -o n:h --long start-node:,no-keep-alive,help -n 'autopilot.sh' -- "$@")
eval set -- "$param"
while true; do
    case "$1" in
    -h | --help)
        Usage
        shift
        exit 0
        ;;
    -n | --start-node)
        opt_onenode=$2
        shift 2
        ;;
    --no-keep-alive)
        opt_alive=0
        shift 1
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
        MOGO_LOG "IINIT_TIME_SYNC" "systime synchronization at $systime"
        echo $systime >$ABS_PATH/launch_time
        break
    fi
    sleep 1
done
curtime=$(date +"%Y%m%d%H%M%S")
LOGFILE="/home/mogo/data/log/autopilot-${curtime}.log"
ERRFILE="/home/mogo/data/log/autopilot-${curtime}.err"
LoggingINFO "systime synchronization at $curtime"
find ${LOG_DIR} -maxdepth 1 -mtime +3 -type d -exec rm -Rf {} \;
find ${LOG_DIR} -name "autopilot-*" -type f -mtime +1 -exec rm -Rf {} \;
find $BAG_DIR -maxdepth 1 -mtime +1 -type d -exec rm -Rf {} \;

[[ ! -d $MOGO_LOG_DIR ]] && mkdir -p $MOGO_LOG_DIR
[ ! -f $MOGO_MSG_CONFIG ] && MOGO_LOG "EINIT_BOOT" "cannot get mogo_msg_config,report could be incompletion"
if [ -z "$opt_onenode" ]; then
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
ethnet_ip=$(ifconfig | grep -v "inet6" | grep -Eo '192[.]168([.][0-9]+){2}' | grep -v "255")
if [ -z "$ethnet_ip" ]; then
    LoggingERR "ip address is null"
    MOGO_LOG "EHW_NET" "ip address is null"
    exit 1
fi
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
set_bashrc
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
# ros日志存储路径的环境变量
export ROS_LOG_DIR
export BAG_DIR="/home/mogo/data/bags"
# ros日志配置文件的环境变量
# export ROSCONSOLE_FORMAT='[${severity}] ${time} [${function}(${line})]:${message}'
export ROSCONSOLE_CONFIG_FILE
export ROS_HOSTNAME=${ros_machine}
export ROS_MASTER_URI=http://${ros_master}:11311
export OMP_NUM_THREADS=1

export BASHRC="source ${SETUP_ROS} && source ${SETUP_AUTOPILOT}"
source $SETUP_ROS
source $SETUP_AUTOPILOT
[[ ! -d $BAG_DIR ]] && mkdir -p $BAG_DIR

get_all_launch_files #获取所有需要启动的launch文件
if [ -n "$opt_onenode" ]; then
    ROS_LOG_DIR=$(readlink ${LOG_DIR}/latest)
    [[ -z "ROS_LOG_DIR" ]] && ROS_LOG_DIR="${LOG_DIR}/$(date +"%Y%m%d_%H%M%S")"
    [[ ! -d $ROS_LOG_DIR ]] && mkdir -p $ROS_LOG_DIR
    ln -snf $ROS_LOG_DIR ${LOG_DIR}/latest
    start_node
    sleep 1
    exit 0
else
    # 自动驾驶自检
    stat_file="/home/mogo/data/vehicle_monitor/check_system.txt"
    while [ true ]; do
        # 运维自检状态
        sleep 1
        if [ -f $stat_file ]; then
            [[ $(head -1 $stat_file) -ne 0 ]] && LoggingERR "system check failed" && continue
        fi
        # python $ABS_PATH/mogodoctor.py c>>$LOGFILE 2>>$ERRFILE
        # if [ $? -eq 0 ]; then
        #     break
        # fi
        # LoggingERR "autopilot check failed"
        break
    done
    python $ABS_PATH/mogodoctor.py c >>$LOGFILE 2>>$ERRFILE
    install_ros_log
    add_privilege_monitor_gnss
    ROS_LOG_DIR="${LOG_DIR}/$(date +"%Y%m%d_%H%M%S")"

fi
[[ ! -d $ROS_LOG_DIR ]] && mkdir -p $ROS_LOG_DIR
ln -snf $ROS_LOG_DIR ${LOG_DIR}/latest
LoggingINFO "ROS_LOG_DIR=$ROS_LOG_DIR"
export LOG_ENV="export GLOG_logtostderr=1; export GLOG_colorlogtostderr=1; export ROS_LOG_DIR=${ROS_LOG_DIR}; export ROS_MASTER_URI=http://${ros_master}:11311; export ROS_HOSTNAME=${ros_machine}"

LoggingINFO "path : $ABS_PATH"
if [ $# -eq 0 ]; then
    LoggingERR "error:请指定车型"
    MOGO_LOG "EVHC_TYPE_UNDEFINED" "undefined vehicle type"
    Usage
    exit 0
fi
LoggingINFO "command : $0 $@"

kill_ros
if [ "$ros_machine" == "$ros_master" ]; then
    start_core
else
    while [ true ]; do
        timeout 1 cat </dev/tcp/${ros_master}/11311
        if [ $? -ne 124 ]; then
            sleep 2
            continue
        fi
        break
    done
    if [ "$ros_machine" == "rosslave" -o "$ros_machine" == "rosslave-103" ]; then
        python2 /home/mogo/autopilot/share/log_reslove/log_reslove.py >/dev/null 2>&1 &
    fi
fi

sleep 1
# 配置更新
timeout 120 roslaunch --wait update_config update_config.launch >$ROS_LOG_DIR/update_config.launch.log 2>$ROS_LOG_DIR/update_config.launch.err

# launch gnss

# launch telematics
ret=$?
if [ $ret -eq 124 ]; then
    LoggingERR "update config timeout"
    MOGO_LOG "EMAP_NODE" "update config timeout"
elif [ $ret -eq 0 ]; then
    MOGO_LOG "IBOOT_CONFIG_UPDATE" "update config finished"
    LoggingINFO "update config finished"
fi

start_node
[[ $opt_alive -ne 0 ]] && keep_alive && LoggingINFO "keep alive is runing..."
