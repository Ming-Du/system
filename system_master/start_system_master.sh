#!/bin/bash 
# the local file is /home/mogo/autopilot/share/system_master/start_system_master.sh

LoggingINFO() {
        datetime=$(date +"%Y-%m-%d %H:%M:%S")
        echo -e "\033[32m[ INFO] [$datetime] $*\033[0m"
        [[ -n "$LOGFILE" ]] && echo "[ INFO] [$datetime] $*" >>$LOGFILE
}

install_ros_log() {
        mkdir -p /home/mogo/data/log/msg_log
        chmod 777 -R /home/mogo/data/log/msg_log
        rm -f /home/mogo/data/log/start_master-*.log
        mv /home/mogo/data/log/system_master.log /home/mogo/data/log/system_master_before.log
        rm -f /tmp/system_state
}

get_xavier_type() {
    # check xavier type
    [ -z "$ethnet_ip" ] && LoggingERR "ip address is null" && exit 1
    ros_machine=$(grep -Eo "^[^#]*$ethnet_ip[[:space:]]*ros[^#]*" /etc/hosts | uniq | head -1 | awk '{print $2}')
    rosmachine=${ros_machine:="localhost"}
    [[ ${rosmachine} == "localhost" ]] && ros_master="${rosmachine}" || ros_master="rosmaster"
    ros_hosts=$(grep -Eo "^[^#]*ros[^#]*" /etc/hosts | uniq | wc -l)
    return $((ros_hosts > 2 ? 3 : ((ros_hosts > 1 ? 2 : 1))))
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

declare -g ros_master ros_machine ethnet_ip
declare -g LOGFILE map_ver
curtime=$(date +"%Y%m%d%H%M%S")
LOGFILE="/home/mogo/data/log/start_master-${curtime}.log"

map_ver=$(/usr/bin/python /home/mogo/autopilot/share/system_master/get_map_version.py)
while [[ "$map_ver" == "unknow" ]]; do
        map_ver=$(/usr/bin/python /home/mogo/autopilot/share/system_master/get_map_version.py)
done
LoggingINFO "get MAP version is $map_ver"
if [[ "$map_ver" != "250" ]]; then
       LoggingINFO "system_master con't run, due map version before 2.5.0"
       exit 1
fi

ethnet_ip=$(ifconfig | grep -v "inet6" | grep -Eo '192[.]168([.][0-9]+){2}' | grep -v "255")
get_xavier_type ## xavier:1x 2x 6x == 1 2 3
declare -g xavier_type=$?
LoggingINFO "rosmachine:${ros_machine} rosmaster:${ros_master} xavier_type:${xavier_type}"

if [[ ${xavier_type} -eq 2 ]]; then
        [[ "${ros_machine}" != "rosslave" ]] && LoggingINFO "2x system_master need run in rosslave" && exit 1
elif [[ ${xavier_type} -eq 3 ]]; then
        [[ "${ros_machine}" != "rosslave-106" ]] && LoggingINFO "6x system_master need run in rosslave-106" && exit 1
fi

export ROS_HOSTNAME=${ros_machine}
export ROS_MASTER_URI=http://${ros_master}:11311
export ROS_ENV="export ROS_LOG_DIR=${ROS_LOG_DIR}; export ROS_MASTER_URI=http://${ros_master}:11311; export ROS_HOSTNAME=${ros_machine}"
install_ros_log
set_bashrc

source /opt/ros/melodic/setup.bash
source /home/mogo/autopilot/setup.bash
source /home/mogo/.bashrc

start_system_pid=$(ps -ef | grep "keep_system_pid_alived_102.sh" |grep -v grep |awk '{print $2}')
if [ -n "$start_system_pid" ]; then
        kill -9 $start_system_pid
fi

LoggingINFO "first time start"
nohup bash /home/mogo/autopilot/share/system_master/keep_system_pid_alived_102.sh >> $LOGFILE 2>&1 &
LoggingINFO "start keep_system_pid_alived success!"
exit 0
