#!/bin/bash

Usage() {
    echo "Usage:"
    echo -e "\t$(basename $0) <VehicleType> [Style] [Options]"
    echo
    echo -e "\t<wey|byd|jinlv|df|hq> [silence|x|g] [[-n|--start-node <node-name>]|[-k|--keep-alive]|[-h|--help]]"
    echo -e "\tVehicleType                    \t\twey:长城 byd:比亚迪 jinlv:小巴 df:东风 hq:红旗 "
    echo -e "\tStyle                          \t\tsilence:后台启动(默认) x:xfce4窗口启动 g:gnome窗口启动"
    echo -e "\tOptions:"
    echo -e "\t\t-n|--start-node <node name>  \t启动单个节点\tnode name 节点名,eg:telematics"
    echo -e "\t\t--pkg <pkg name>  \t指定package,需要与--launch-file同时使用\tpkg name 包名,eg:telematics"
    echo -e "\t\t--launch-file <launch file name>  \t指定launch文件,需要与--pkg同时使用\tnode-name launch文件名,eg:telematics.launch"
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
    echo -e "\t|$(basename $0) hq --pkg hadmap_engine --launch-file hadmap_engine.launch"
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
    if [[ $(grep -c "\. /usr/share/bash-completion/completions/autopilot_completion" ~/.bashrc) -eq 0 ]];then
        echo ". /usr/share/bash-completion/completions/autopilot_completion" >>~/.bashrc
    fi
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
        if [[ $(grep -c "\. /usr/share/bash-completion/completions/autopilot_completion" /home/mogo/.bashrc) -eq 0 ]];then
            echo ". /usr/share/bash-completion/completions/autopilot_completion" >> /home/mogo/.bashrc
        fi
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
    sync
}

get_launch_files() {
    local file_set
    if [[ ! -f $1 || $(sed '/^\s*$/d' $1 | wc -m) -eq 0 ]]; then
        LoggingERR "list file:$1 doesn't exist or it's empty" "EINIT_LOST_FILE"
        return -1
    fi
    local ret=0
    while read launch_file || [[ -n $launch_file ]]; do
        # 读取到空行
        [[ -z "$launch_file" ]] && continue
        [[ $(echo $launch_file | awk '{print NF}') -eq 1 ]] && real_file=$launch_file || real_file=$(roscd ${launch_file% *} && find ${PWD} -name ${launch_file#* })
        # 找不到launch文件
        [[ ! -f $real_file ]] && ((ret+=1)) && LoggingERR "cannot locate $launch_file" "EINIT_LOST_FILE" && continue
        [[ -z "$(xmllint --xpath "//include/@file" $real_file 2>/dev/null)" ]] && include_files=$real_file || include_files=$(roslaunch --files $real_file 2>/dev/null)
        local should_start_list=""
        for child_file in $include_files; do
            [[ -z "$child_file" ]] && continue
            [[ $(echo $file_set | grep -w -c "$child_file:") -ne 0 ]] && continue
            type_name=$(xmllint --xpath "//node[@pkg!='rviz']/@type" $child_file 2>/dev/null | sed 's/\"//g')
            [[ -z "$type_name" ]] && continue
            should_start_list=$should_start_list:$child_file
            if [[ ! -z "$(xmllint --xpath "//include/@file" $child_file 2>/dev/null)" ]]; then
                for f in $(roslaunch --files $child_file); do
                    [[ $(echo $file_set | grep -w -c "$f:") -ne 0 ]] && continue
                    file_set="$f:$file_set"
                    [[ "$f" != "$child_file" ]] && should_start_list=$(echo ${should_start_list} | sed "s#:*$f##g")
                done
            fi
        done
        for v in $(echo ${should_start_list//:/ }); do
            [[ $(echo ${launch_files_array[@]} | grep -wc $v) -eq 0 ]] && launch_files_array+=("$v")
        done
    done <$1
    return $ret
}

get_sys_launch_files() {
    launch_files_array=()
    sys_launch_files_array=()
    get_launch_files $sys_list_file
    ret=$?
    sys_launch_files_array+=(${launch_files_array[@]})
    return $ret
}
get_map_launch_files() {
    launch_files_array=()
    map_launch_files_array=()
    get_launch_files $map_list_file
    ret=$?
    map_launch_files_array+=(${launch_files_array[@]})
    return $ret
}

start_onenode() {
    local real_launch_file="$1"
    . $ABS_PATH/add_log_config.sh "$real_launch_file" INFO
    # LoggingINFO "launching ${real_launch_file}..."
    launch_file=$(echo $real_launch_file | awk '{print $NF}' | awk -F/ '{print $NF}')
    local child_pid
    if [ "$GuiServer" == "silence" ]; then
        roslaunch $launch_prefix $real_launch_file >/dev/null 2>&1 &
        child_pid=$!
    else
        $GuiTerminal --tab -e "bash -c 'sleep 3; $BASHRC && roslaunch $launch_prefix $real_launch_file >/dev/null 2>&1';bash" $TitleOpt "${launch_file}" &
    fi
    [[ $2 == "MAP" ]] && map_pid_name[$child_pid]=${launch_file} || sys_pid_name[$child_pid]=${launch_file}
}

set_pr() {
    while [ $exit_flag -ne 1 ] ;do
        rt_node_array=`rosnode list | tr "\n" " "`
        sleep 2
        for t in ${rt_node_array[@]}; do
            t=${t##*/}
            [[ "$t" =~ "rviz" ]] && continue
            [[ "$t" =~ "update_map" ]] && continue
            #pr
            pids=$(ps -ef | grep "__name:=$t" | grep -v grep | awk '{print $2}')
            [[ -z "$pids" ]] && continue
            for pid in ${pids}; do
                [[ -z "$pid" ]] && continue
                priority=$(top -b -n 1 -p $pid | tail -n 1 | awk '{print $(NF-9)}')
                [[ "$priority" == "rt" ]] && continue
                case "$t" in
                "M1_can_adapter" | "jinlv_can_adapter" | "M2_can_adapter")
                    (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 45 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "controller") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 44 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "localization" | "drivers_gnss" | "drivers_gnss_zy") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 42 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "local_planning") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 40 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "perception_fusion_mid") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 29 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "hadmap_server" | "hadmap_engine_node") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 30 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "perception_fusion2" | "perception_fusion") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 30 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "rs_perception_node" | "rs_perception_zvision_node") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 20 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "xiaoba_lidars_fusion" | "xiaoba_rslidars_fusion") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 15 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "c32_rear_decoder" | "c32_left_decoder" | "c32_right_decoder") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 11 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "drivers_robosense_node" | "c32_rear_driver" | "c32_left_driver" | "c32_right_driver") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 10 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                "rslidar_left" | "rslidar_rear" | "rslidar_right" | "zvision_lidar_front_nodelet_manager" | "zvision_lidar_front_nodelet_manager_driver" | "zvision_lidar_front_nodelet_manager_cloud" | "zvision_lidar_left_nodelet_manager" | "zvision_lidar_left_nodelet_manager_driver" | "zvision_lidar_left_nodelet_manager_cloud" | "zvision_lidar_right_nodelet_manager" | "zvision_lidar_right_nodelet_manager_driver" | "zvision_lidar_right_nodelet_manager_cloud" | "zvision_lidar_rear_nodelet_manager" | "zvision_lidar_rear_nodelet_manager_driver" | "zvision_lidar_rear_nodelet_manager_cloud" | "xiaoba_zvisionlidars_fusion") (($priority >= 0)) && (taskset -a -cp 1-7 $pid && chrt -a -p -r 10 $pid || LoggingERR "set priority of $t[pid:$pid] failed") ;;
                *) ;;
                esac
            done
        done
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
    [ -z "$ethnet_ip" ] && LoggingERR "ip address is null" && exit 1
    ros_machine=$(grep -Eo "^[^#]*$ethnet_ip[[:space:]]*ros[^#]*" /etc/hosts | uniq | head -1 | awk '{print $2}')
    rosmachine=${ros_machine:="localhost"}
    [[ ${rosmachine} == "localhost" ]] && ros_master="${rosmachine}" || ros_master="rosmaster"
    ros_hosts=$(grep -Eo "^[^#]*ros[^#]*" /etc/hosts | uniq | wc -l)
    ((ros_hosts == 0)) && xavier_type="1x" || xavier_type="${ros_hosts}x"
    # return $((ros_hosts > 2 ? 3 : ((ros_hosts > 1 ? 2 : 1))))
}

generate_list() {
    local file_name=""
    if [ ! -z "$opt_launch_file" ]; then
        echo "$opt_pkg $opt_launch_file" | sed 's/^\s*//g' >/tmp/tmp.list
        LoggingINFO "start list file:/tmp/tmp.list"
    else
        map_list_file="${ABS_PATH}/config/MAP_${VehicleType}_${ros_machine}_${xavier_type}.list"
        sys_list_file="${ABS_PATH}/config/SYS_${VehicleType}_${ros_machine}_${xavier_type}.list"
        if [[ -f $ABS_PATH/parse_list.py ]];then
            python $ABS_PATH/parse_list.py $VehicleType $ros_machine $xavier_type "SYS"
            python $ABS_PATH/parse_list.py $VehicleType $ros_machine $xavier_type "MAP"
        fi
        LoggingINFO "map list file:${map_list_file}    sys list file:${sys_list_file}"
    fi
    list_file="/tmp/tmp.list"
}

install_ros_log() {
    [[ ! -d /autocar-code/install ]] && return
    mkdir -p /home/mogo/data/log/ROS_STAT/
    mkdir -p /home/mogo/data/log/ROS_STAT/EXPORT/
    chmod 777 -R /home/mogo/data/log/
    roscore_xml_path=$(find /autocar-code/install/ -name 'roscore.xml' | head -n 1)
    if [ -n "$roscore_xml_path" ];then
        \cp -rf $roscore_xml_path  /opt/ros/melodic/etc/ros/roscore.xml
        \cp -rf $roscore_xml_path  /opt/ros/melodic/share/roslaunch/resources/roscore.xml
    fi
    [[ -f /usr/bin/rosversion ]] && \mv /usr/bin/rosversion  /usr/bin/rosversion_backup
}

add_privilege_monitor_gnss() {
    [[ ! -d /autocar-code/install ]] && return
    #rm /home/mogo/data/log/location.txt -rf
    #rm /home/mogo/data/log/msg_info_log.txt -rf
    #rm /home/mogo/data/log/msg_error_log.txt -rf
    #rm /home/mogo/data/log/topic_hz_log.txt -rf
    rm -rf /home/mogo/data/log/filebeat_upload/*
    chmod -R 777 /autocar-code/install/share/monitor_gnss >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/share/monitor_collect >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/share/monitor_process >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/share/hd_map_agent  >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/share/trajectory_agent  >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/lib/drivers_innolidar  >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/lib/zvision_lidar_driver  >/dev/null 2>&1
    chmod -R 777 /autocar-code/install/share/update_config_simple  >/dev/null 2>&1
}

_md5cmp() {
    [[ $# -ne 2 ]] && LoggingERR "_md5cmp expect two arguments" && return 1
    [ ! -f $1 -o ! -f $2 ] && return 1
    md5_1=$(md5sum $1 | awk '{print $1}')
    md5_2=$(md5sum $2 | awk '{print $1}')
    return $(test $md5_1 == $md5_2)
}

_update() {
    install_ros_log
    if [[ ! -f ${ABS_PATH}/update/updated.flag ]]; then
        [[ ! -d ${ABS_PATH}/update/old ]] && mkdir -p ${ABS_PATH}/update/old
        while read src_to_dest || [[ ! -z "$src_to_dest" ]]; do
            [[ ! -d ${ABS_PATH}/update/new ]] && break
            local target_file=${src_to_dest% *}
            local target_dir=${src_to_dest#* }
            _md5cmp "${ABS_PATH}/update/new/${target_file}" "${target_dir}/${target_file}"
            if [ $? -ne 0 ];then
                [[ ! -d ${target_dir} ]] && mkdir -p ${target_dir}
                #备份旧文件
                [[ -f ${target_dir}/${target_file} ]] && mv ${target_dir}/${target_file} ${ABS_PATH}/update/old/${target_file}
                cat ${ABS_PATH}/update/new/${target_file} > ${target_dir}/${target_file}
                sync
                #检查是否更新成功
                _md5cmp "${ABS_PATH}/update/new/${target_file}" "${target_dir}/${target_file}"
                if [ $? -eq 0 ];then
                    LoggingINFO "update ${target_file} succeed"
                else
                    LoggingERR "update ${target_file} failed"
                fi
            fi
        done <${ABS_PATH}/update/update.list
    fi
}
start_core() {
    core_stat=0 && write_action
    [[ -n "$opt_onenode" || -n "$opt_launch_file" ]] && return 1
    [[ "$ros_machine" != "$ros_master" ]] && return 1
    kill_ros
    LoggingINFO "starting roscore..."
    roscore >$ROS_LOG_DIR/roscore.log 2>&1 & 
    roscore_pid=$!
    local ret=0
    local deadtime=$(($(date +"%s")+10))
    while [[ $ret -ne 124 && $(date +"%s") -le $deadtime ]]; do
        timeout 0.2 cat &>/dev/null </dev/tcp/${ros_master}/11311
        ret=$?
    done
    local rosmaster_pid
    if [ $ret -eq 124 ]; then
        rosmaster_pid=$(ps -ef | grep -w "rosmaster --core" | grep -v grep | awk '{print $2}')
        LoggingINFO "starting roscore finished,rosmaster pid:$rosmaster_pid"
        taskset -a -cp 1-7 $rosmaster_pid && chrt -a -p -r 20 $rosmaster_pid 2>/dev/null
        core_stat=1 && write_action
    else
        LoggingERR "starting roscore failed:\n$(cat $ROS_LOG_DIR/roscore.log)" "EMAP_NODE"
        return 1
    fi
    return 0
}
kill_ros() {
    core_pid=$(ps aux | grep -v grep | grep -w "rosmaster --core" | awk '{print $2}')
    [[ ! -z "$core_pid" ]] && LoggingINFO "killing roscore..." && kill -2 $core_pid >/dev/null 2>&1
    core_stat=0 && write_action
}
wait_core() {
    LoggingINFO "waiting roscore in ${ros_master:="localhost"}..."
    local ret=0
    while [ $ret -ne 124 -a $exit_flag -eq 0 ]; do
        timeout 1 cat &>/dev/null </dev/tcp/${ros_master}/11311
        ret=$?
    done
    core_stat=1 && write_action
}

write_action() {
    [[ ! -z "$opt_launch_file" || ! -z "$opt_onenode" ]] && return
    old_action=$(read_action)
    old_action=${old_action:-"000"}
    [[ $old_action -eq ${core_stat}${sys_stat}${map_stat} ]] && return
    flock -x 9
    echo ${core_stat}${sys_stat}${map_stat} >$action_file
    flock -u 9
    return 0
}

read_action() {
    flock -s 9
    echo $(head -1 ${action_file})
    flock -u 9
}
# command type
# 0 - invalid
# 1 - roscore starting
# 2 - roscore started
# 3 - roscore stopping
# 4 - roscore stopped
# 5 - nodes starting
# 6 - nodes started
# 7 - nodes partial started
# 8 - nodes stopping
# 9 - nodes stopped
# 10 - map started
# signal 34 -- start map
# signal 35 -- stop map

# 状态字段:
# 第一个字节:roscore状态
# 第二个字节:其他节点状态
# 第三个字节:map节点状态

# 状态值
# 0:未启动
# 1:全部启动
# 2:部分启动
command_handler() {
    local type=$1
    LoggingINFO "receive ${type} command from master"
    local action=$(read_action)
    local _core_action=${action:0:1}
    local _sys_action=${action:1:2}
    local _map_action=${action:2:3}
    case "$type" in
    "start_sys") 
        # only valid when status is stopped or unknown
        ((_sys_action==1)) && LoggingERR "The operation[${type}] hasn't been executed because the sys nodes had be launched" "EAGENT_MASTER_COMMAND_HANDLER_FAILED" && return 1
        start_sys
        ;;
    "stop_sys") 
        ((_sys_action==0)) && LoggingERR "The operation[${type}] hasn't been executed because the sys nodes hadn't be launched" "EAGENT_MASTER_COMMAND_HANDLER_FAILED" && return 1
        stop_sys
        ;;
    "start_map") 
        # only valid when status is stopped or unknown
        ((_map_action==1)) && LoggingERR "The operation[${type}] hasn't been executed because the map nodes had be launched" "EAGENT_MASTER_COMMAND_HANDLER_FAILED" && return 1
        start_map
        ;;
    "stop_map") 
        ((_map_action==0)) && LoggingERR "The operation[${type}] hasn't been executed because the sys nodes hadn't be launched" "EAGENT_MASTER_COMMAND_HANDLER_FAILED" && return 1
        stop_map
        ;;
    *) LoggingERR "unknown command type:${type}" "EAGENT_MASTER_COMMAND_HANDLER_FAILED" && return 1 ;;
    esac
    LoggingINFO "execute ${type} command successfully" "IAGENT_EXECUTE_MASTER_COMMAND"

}

start_sys() {
    sys_pid_name=()
    LoggingINFO "starting SYS nodes..."
    wait_core
    get_sys_launch_files #获取所有需要启动的launch文件
    failed_files_num=$?
    ((failed_files_num==255)) && return $failed_files_num
    sys_child_node_array+=($(roslaunch --nodes ${sys_launch_files_array[*]}))
    for launch_cmd in ${sys_launch_files_array[*]}; do
        start_onenode "$launch_cmd" "SYS"
    done
    python $ABS_PATH/mogodoctor.py c >/dev/null 2>&1
    if [[ $failed_files_num -ne 0 ]]; then
        sys_stat=2 && write_action
        LoggingERR "partial SYS nodes launched failed."
        return 0
    fi
    sleep 2 
    if [[ $(ps -p ${!sys_pid_name[@]} | sed '1d' | wc -l) -lt ${#sys_pid_name[@]} ]];then 
        sys_stat=2 && write_action
        for p in ${!sys_pid_name[@]};do
            [[ $(ps -p $p | sed '1d' | wc -l) -lt 1 ]] && LoggingERR "SYS node[${sys_pid_name[${p}]}] launched failed." || continue
        done
        LoggingERR "partial SYS nodes launched failed."
    else
        sys_stat=1 && write_action
        LoggingINFO "All SYS nodes in launched successfully."
    fi
}

start_map() {
    map_pid_name=()
    LoggingINFO "starting MAP nodes..."
    wait_core
    get_map_launch_files #获取所有需要启动的launch文件
    failed_files_num=$?
    ((failed_files_num==255)) && return $failed_files_num
    map_child_node_array+=($(roslaunch --nodes ${map_launch_files_array[*]}))
    for launch_cmd in ${map_launch_files_array[*]}; do
        start_onenode "$launch_cmd" "MAP"
    done
    if [[ $failed_files_num -ne 0 ]]; then
        map_stat=2 && write_action
        LoggingERR "${ros_machine} Started finished with partial nodes failure." "EMAP_NODE"
        return 0
    fi
    sleep 2 
    if [[ $(ps -p ${!map_pid_name[@]} | sed '1d' | wc -l) -lt ${#map_pid_name[@]} ]];then 
        map_stat=2 && write_action
        for p in ${!map_pid_name[@]};do
            [[ $(ps -p $p | sed '1d' | wc -l) -lt 1 ]] && LoggingERR "MAP node[${map_pid_name[${p}]}] launched failed." "EMAP_NODE" || continue
        done
    else
        map_stat=1 && write_action
        LoggingINFO "All MAP nodes in ${ros_machine} launched successfully." "IBOOT_MAP_STARTED" 
    fi
}

stop_sys() {
    LoggingINFO "stopping SYS nodes..." 
    echo ${!sys_pid_name[@]} | xargs kill -2 >/dev/null 
    LoggingINFO "stop SYS nodes finished..." 
    sys_stat=0 && write_action
}

stop_map() {
    LoggingINFO "stopping MAP nodes..." 
    echo ${!map_pid_name[@]} | xargs kill -2 >/dev/null 
    LoggingINFO "stop MAP nodes finished..." 
    map_stat=0 && write_action
}

check_child_stat(){
    ((map_stat==0&&sys_stat==0)) && return
    if [[ $map_stat -ne 0 ]];then
        for pid in ${!map_pid_name[@]};do
            if [[ $(ps -p ${pid} | sed '1d' | wc -l) -eq 0 ]]; then
                LoggingINFO "${map_pid_name[$pid]}[${pid}] exited"
                unset map_pid_name[$pid] 
                ((map_stat==1)) && map_stat=2 && write_action
            fi
        done
    fi
    if [[ $sys_stat -ne 0 ]];then
        for pid in ${!sys_pid_name[@]};do
            if [[ $(ps -p ${pid} | sed '1d' | wc -l) -eq 0 ]]; then
                LoggingINFO "${sys_pid_name[$pid]}[${pid}] exited"
                unset sys_pid_name[$pid] 
                ((sys_stat==1)) && sys_stat=2 && write_action
            fi
        done
    fi
}

heart_beat() {
    [[ -n "$opt_onenode" || -n "$opt_launch_file" ]] && return
    while [[ $exit_flag -eq 0 ]]; do
        action=$(read_action)
        timeout 5 curl -d "action=${action-"000"},time=$(date +"%s").$(($(echo $(date +"%N") | sed 's/^0*//') / 1000000))" $master_ip:8080 >/dev/null 2>&1
        [[ $? -eq 124 ]] && LoggingERR "cannot connect with master" && continue
        sleep 1
    done
}

_exit() {
    LoggingINFO "autopilot shut down"
    jobs -p | xargs kill -15 >/dev/null 2>&1
    action=$(read_action)
    timeout 2 curl -d "action=${action-0},time=$(date +"%s").$(($(echo $(date +"%N") | sed 's/^0*//') / 1000000))" $master_ip:8080 >/dev/null 2>&1
}

# main
trap 'LoggingINFO "receive SIGINT/SIGTERM signal";exit_flag=1' INT TERM
trap '_exit' EXIT
trap 'check_child_stat' CHLD
trap 'command_handler "start_sys"' USR1
trap 'command_handler "stop_sys"' USR2
trap 'command_handler "start_map"' 34
trap 'command_handler "stop_map"' 35
export ABS_PATH # autopilot.sh脚本的路径
ABS_PATH="$(cd "$(dirname $0)" && pwd)"

echo 0 > /proc/sys/vm/swappiness
echo 500 > /proc/sys/vm/watermark_scale_factor
echo 5 > /proc/sys/vm/dirty_background_ratio
echo 60 > /proc/sys/vm/dirty_ratio

declare -A -g map_pid_name=() sys_pid_name=()
declare -g launch_files_array=() map_launch_files_array=() sys_launch_files_array=()
declare -g map_child_node_array=() sys_child_node_array=()
declare -g opt_onenode opt_pkg opt_launch_file opt_log_level
declare -g LOG_DIR="/home/mogo/data/log"
declare -g BAG_DIR="/home/mogo/data/bags"
declare -g -r MOGO_MSG_CONFIG="$ABS_PATH/config/mogo_report_msg.json"
declare -g -r MOGO_LOG_DIR="$LOG_DIR/msg_log"
declare -g -r MOGOLOGFILE="$MOGO_LOG_DIR/autopilot_report.json"
declare -g -r LOGFILE="/home/mogo/data/log/autopilot.log" #
declare -g -r ERRFILE="/home/mogo/data/log/autopilot.err" #
declare -g exit_flag=0 map_list_file sys_list_file roscore_pid ros_master ros_machine
declare -g -r action_file=${ABS_PATH}/agent_action.data
declare -g xavier_type
declare -g vehicle_property launch_prefix="--wait"
declare -g master_ip
declare -i -g core_stat=0 sys_stat=0 map_stat=0

exec 6>>$LOGFILE
exec 7>>$ERRFILE
exec 8>>/home/mogo/data/launch_time
exec 9>$action_file
self_pid=$$
ethnet_ip=$(ifconfig | grep -v "inet6" | grep -Eo '192[.]168([.][0-9]+){2}' | grep -v "255")
this="[$ethnet_ip] ${ABS_PATH}/$(basename $0)"
args="$@"

param=$(getopt -a -o f:n:P:N:h --long list-file:,start-node:,pkg:,launch-file:,no-keep-alive,help -n 'autopilot.sh' -- "$@")
eval set -- "$param"
while true; do
    case "$1" in
    -h | --help) Usage && exit 0 ;;
    --launch-file) opt_launch_file=$2 && shift 2 ;;
    -n | --start-node) opt_onenode=$2 && shift 2 ;;
    --pkg) opt_pkg=$2 && shift 2 ;;
    --node-log-level) opt_log_level=$2 && shift 2 ;;
    --) shift && break ;;
    *) echo "error" && exit 1 ;;
    esac
done
#参数合法性判断
[[ -n "$opt_launch_file" ]] && declare -g -r model=" [${opt_pkg:-"$opt_launch_file"}]" || declare -g -r model=" [MAP]"
[[ -z "$opt_launch_file" && ! -z "$opt_pkg" ]] && LoggingERR "'--pkg' must be used with '--launch-file' together" && exit 1
[[ ! -z "$opt_launch_file" && ! -z "$opt_onenode" ]] && LoggingERR "'--launch-file' cannot use with '--start-node'" && exit 1
[[ ! -d $LOG_DIR ]] && mkdir -p $LOG_DIR
[[ ! -d $BAG_DIR ]] && mkdir -p $BAG_DIR
chown -R mogo:mogo $BAG_DIR
[[ ! -d $MOGO_LOG_DIR ]] && mkdir -p $MOGO_LOG_DIR
[[ ! -d ${ABS_PATH/}config ]] && mkdir -p ${ABS_PATH}/config

# GuiServer:silence -- 后台启动 xfce4 -- docker中启动 终端使用xfce4-terminal gnome -- 宿主机中启动 终端使用gnome-terminal
export GuiServer=${2:-silence}
export VehicleType=$1  # VehicleType    wey jinlv byd df ...
export GuiTerminal     # 使用的terminal程序的绝对路径，如/usr/bin/xfce4-terminal
export TitleOpt        # 指定terminal窗口标题的选项，xfce为'-T'，gnome为'-t'
export SETUP_ROS       # ros系统自带的setup.bash路径，一般位于/opt/ros/melodic/setup.bash
export SETUP_AUTOPILOT # 用户程序的setup.bash
export VEHICLE_PLATE
export JINLV_SUBTYPE
if [ -f /home/mogo/data/vehicle_monitor/vehicle_config.txt ]; then
    VEHICLE_PLATE=$(grep plate /home/mogo/data/vehicle_monitor/vehicle_config.txt | awk -F: '{print $2}' | sed -e 's/ //g' -e 's/\"//g')
    [[ -z "$VEHICLE_PLATE" ]] && LoggingERR "cannot read /home/mogo/data/vehicle_monitor/vehicle_config.txt" "EINIT_LOST_FILE"
    [[ ! -z "$VEHICLE_PLATE" ]] && ln -snf /home/mogo/data/vehicle_monitor/${VEHICLE_PLATE} /home/mogo/autopilot/share/config/vehicle 2>/dev/null
fi

if [ -f /home/mogo/autopilot/share/config/vehicle/vehicle_config.txt ]; then
    JINLV_SUBTYPE=$(grep subtype /home/mogo/autopilot/share/config/vehicle/vehicle_config.txt | awk -F: '{print $2}' | sed -e 's/ //g' -e 's/\"//g')
    if [ ! -z "$JINLV_SUBTYPE" ]; then
      JINLV_SUBTYPE_FLAG=$(grep "export\b[[:space:]]*JINLV_SUBTYPE" ~/.bashrc | grep -v "^#" | tail -1)
      if [ -z "$JINLV_SUBTYPE_FLAG" ]; then
        echo "export JINLV_SUBTYPE=$JINLV_SUBTYPE" >>~/.bashrc
      fi
    fi
fi

vehicletypes="wey df hq byd jinlv kaiwo"
[[ -z "$opt_launch_file" && (-z "$VehicleType" || $(echo $vehicletypes | grep -wc $VehicleType) -lt 1) ]] && LoggingERR "vehicle type undefined" && Usage && exit 1
if [ -z /autocar-code/install/share/log_reslove/config.py ]; then
    ln -snf /autocar-code/install/share/log_reslove/config_$VehicleType.py /autocar-code/install/share/log_reslove/config.py
    [[ -z /autocar-code/install/share/log_reslove/config.py ]] && LoggingERR "create log_reslove/config.py error!"
fi
[ ! -f $MOGO_MSG_CONFIG ] && LoggingERR "cannot get mogo_msg_config,report could be incompletion" "EINIT_LOST_FILE"
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
get_xavier_type #获取xavier类型:1x 2x 6x
generate_list #生成list
LoggingINFO "rosmachine:${ros_machine} rosmaster:${ros_master} xavier type:$xavier_type"
LoggingINFO "cwd:$ABS_PATH    command:$0 $args"
export ROSCONSOLE_CONFIG_FILE
export ROS_PYTHON_LOG_CONFIG_FILE
export ROS_HOSTNAME=${ros_machine}
export ROS_MASTER_URI=http://${ros_master}:11311
export OMP_NUM_THREADS=1
export BASHRC="source ${SETUP_ROS} && source ${SETUP_AUTOPILOT}"
export ROS_ENV="export ROS_LOG_DIR=${ROS_LOG_DIR}; export ROS_MASTER_URI=http://${ros_master}:11311; export ROS_HOSTNAME=${ros_machine}"
export JINLV_SUBTYPE=${JINLV_SUBTYPE}
_update
set_bashrc
#获取车辆用途
\rm -rf /home/mogo/data/vehicle_use.info.error
\rm -rf /home/mogo/data/vehicle_use.info
try_times=0
while true
do
    vehicle_path=`find /autocar-code/install/share/ -name vehicle_init.py | head  -n 1`
    [[ -f $vehicle_path ]] && python  $vehicle_path || break
    if [ -e "/home/mogo/data/vehicle_use.info" ];then
        echo "found"
        break
    fi
    try_times=`expr $try_times + 1`
    echo $try_times
    if [  $try_times -eq 5 ];then
        echo "try times eq 5 times,abort get vehicle use" >> /home/mogo/data/vehicle_use.info.error
        break
    fi
    sleep 3
done
if [ ! -e "/home/mogo/data/vehicle_use.info" ];then
        echo "not exists"
        echo  "{\"cannot access url\"}" >>  /home/mogo/data/vehicle_use.info.error
fi
python ${ABS_PATH}/vehicle_init.py
vehicle_property=$?
LoggingINFO "current property of $VEHICLE_PLATE is $vehicle_property"
((vehicle_property==3||vehicle_property==4)) && launch_prefix="$launch_prefix --respawn"
# [[ "${ros_machine}" == "${ros_master}" && -z "$opt_launch_file" ]] && bash ${ABS_PATH}/../system_master/start_system_master.sh
if [[ ${xavier_type} == "2x" ]]; then
    master_ip=${ethnet_ip%.*}.103
elif [[ ${xavier_type} == "6x" ]]; then
    master_ip=${ethnet_ip%.*}.106
else
    master_ip=${ethnet_ip%.*}.102
fi

write_action
# 后台发送心跳
# heart_beat &
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
        last_launch_time=$(date +"%F %T")
        echo $systime >$ABS_PATH/launch_time
        if [[ -z "$opt_onenode" && -z "$opt_launch_file" ]]; then
            LoggingINFO "systime synchronization at $systime" "IINIT_TIME_SYNC"
            LoggingINFO "boot:$(date -d "$(uptime -s)" +"%F %T")" "IINIT_BOOST" #上电时间
        fi
        break
    fi
    sleep 1
done
#清理旧autopilot.log&err日志
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
# ros日志存储路径的环境变量
export ROS_LOG_DIR="${LOG_DIR}/$(date +"%Y%m%d")"
LoggingINFO "ROS_LOG_DIR=$ROS_LOG_DIR"
flock -x 8
if [[ ! -d $ROS_LOG_DIR ]]; then
    find ${LOG_DIR} -maxdepth 1 -mtime +10 -type d -exec rm -Rf {} \;
    find ${LOG_DIR}/tracing_log -mindepth 1 -maxdepth 1 -mtime +7 -type d -exec rm -Rf {} \;
    find $BAG_DIR -maxdepth 10 -mtime +10 -exec rm -Rf {} \;
    mkdir -p $ROS_LOG_DIR
    ln -snf $ROS_LOG_DIR ${LOG_DIR}/latest
fi
flock -u 8
if [[ -n "$opt_onenode" || -n "$opt_launch_file" ]];then
    local real_launch_file
    if [ -n "$opt_launch_file" ];then
        real_launch_file="$opt_pkg $opt_launch_file"
    elif [ -n "$opt_onenode" ];then 
        [[ ${opt_onenode:0:1}=='/' ]] && real_launch_file=$opt_onenode || real_launch_file=$(grep -w $opt_onenode $list_file)
        if [[ -z $real_launch_file ]]; then
            real_launch_file=$(grep -w $opt_onenode ${ABS_PATH}/*.list | head -1)
            if [ -z $real_launch_file ]; then
                local multy_machine
                [[ $ros_machine == "rosmaster" ]] && multy_machine="rosmaster-102" || multy_machine=$ros_machine
                LoggingERR "cannot find $opt_onenode,you can take one of the follow actions to fix this problem:
                1.add the launching command into ${ABS_PATH}/*.list,1X into all.list,2X into ${ros_machine}.list,others into ${multy_machine}.list.
                    e.g.:if the command is \"roslaunch launch local_planning.launch\",add \"launch local_planning.launch\" to list
                        :if the command is \"roslaunch /home/mogo/autopilot/share/launch/local_planning.launch\",add \"/home/mogo/autopilot/share/launch/local_planning.launch\" to list
                2.using completed path of launch file replaced after -n|--start-node option.
                    e.g.:/home/mogo/autopilot/share/launch/local_planning.launch.
                "
                exit 0
            fi
        fi
    fi
    
    . $ABS_PATH/add_log_config.sh $real_launch_file INFO
    LoggingINFO "launching ${real_launch_file}..."
    launch_file=$(echo $real_launch_file | awk '{print $NF}' | awk -F/ '{print $NF}')
    nohup roslaunch $launch_prefix $launch_cmd &
    [ $? -eq 0 ] && LoggingINFO "launched $launch_cmd successfully" || LoggingERR "launched $launch_cmd failed"
    tail -f /dev/null
    trap EXIT
    exit 0
fi
pids=$(ps -ef | grep -w "autopilot\.sh" | grep -v grep | awk '!($3 in arr) && $2 != "'$self_pid'" && $3 != "'$self_pid'" {arr[$2]=$2};END{for(idx in arr){print arr[idx]}}')
for pid in $pids; do [[ "$pid" != "$self_pid" ]] && LoggingINFO "clean exist $(basename $0)[$pid]" && kill -2 $pid; done
# 备份filebeat文件
filebeat_backup="/home/mogo/data/log/filebeat_backup"
mkdir -p ${filebeat_backup}
FileBackPath_arry=("/home/mogo/data/log/filebeat_upload/tele_stat.log" "/home/mogo/data/log/filebeat_upload/new_topic_hz_log.log"  "/home/mogo/data/log/filebeat_upload/msg_record.log")
for FileBackPath in ${FileBackPath_arry[@]}; do
    if [ -e "$FileBackPath" ]; then
        cp_file_name=${FileBackPath##*/}
        cp  "$FileBackPath"  "${filebeat_backup}/${cp_file_name}$(date +_%Y-%m-%d_%H_%M_%S)"
    fi
done

add_privilege_monitor_gnss
start_core
LoggingINFO "update config...."
rm -rf  /home/mogo/data/config_end
. $ABS_PATH/add_log_config.sh update_config_simple.launch INFO
timeout 300 roslaunch --wait update_config_simple  update_config_simple.launch >$ROS_LOG_DIR/update_config.launch.log 2>&1
LoggingINFO "update config finished"
if [ -f "/home/mogo/autopilot/share/hadmap_engine/data/hadmap_data/db.sqlite.backup" ];then
 \cp -d /home/mogo/autopilot/share/hadmap_engine/data/hadmap_data/db.sqlite.backup /home/mogo/autopilot/share/hadmap_engine/data/hadmap_data/db.sqlite
fi
monitor_shell=/home/mogo/autopilot/share/system_monitor/monitor_cpu_mem_net/monitor_cpu_mem_net.sh
chmod +x $monitor_shell
bash $monitor_shell &
python3 /home/mogo/autopilot/share/system_monitor/disk_manage/disk_manage.py >> /home/mogo/data/log/disk_manage.log 2>&1 &

request_master_mes=$(curl -d -m 10 -o /dev/null -s http://${master_ip}:8080/report_config)
# 等待systerm master响应
while [ -z "$request_master_mes" ]; do
    sleep 1
    request_master_mes=$(curl -d -m 10 -o /dev/null -s http://${master_ip}:8080/report_config)
    LoggingINFO "waitting for systerm master running!"
done
LoggingINFO "ssm ret=$request_master_mes"
old_rquest_master_mes="The datas used fault format"
# 判断是否走新agent
if [[ $request_master_mes =~ $old_rquest_master_mes ]]; then
    # old agent
    # 后台发送心跳
    heart_beat &
    LoggingINFO "use old agent!!!!!!!"
    start_sys
    start_map
else
    # new agent
    LoggingINFO "use new agent!!!!!!!"
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple psutil
    wait_core
    python3 /home/mogo/autopilot/share/system_monitor/ssm_agent/ssm_agent.py $ABS_PATH $ROS_LOG_DIR >> /dev/null 2>&1 &
fi



set_pr

