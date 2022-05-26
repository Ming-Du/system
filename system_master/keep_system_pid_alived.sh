#!/bin/bash

check_pid()
{
sysmaster_pid=$(ps -ef | grep system_master |grep -v grep |awk '{print $2}')
if [ -z $sysmaster_pid ]; then
	cd /home/liyl/catkin_ws/src/system/system_master
	nohup python -u system_master.py >> /home/mogo/data/log/system_master.log 2>&1 &
fi
}

LoggingINFO() {
        datetime=$(date +"%Y-%m-%d %H:%M:%S")
        echo -e "\033[32m[ INFO] [$datetime] $*\033[0m"
        [[ -n "$LOGFILE" ]] && echo "[ INFO] [$datetime] $*" >>$LOGFILE
}

install_ros_log() {
        mkdir -p /home/mogo/data/log/
        chmod 777 -R /home/mogo/data/log/
}
declare -g LOGFILE
declare -g ERRFILE
declare -g LOG_DIR="/home/mogo/data/log"
curtime=$(date +"%Y%m%d%H%M%S")
LOGFILE="/home/mogo/data/log/autopilot-${curtime}.log"
ERRFILE="/home/mogo/data/log/autopilot-${curtime}.err"

install_ros_log
LoggingINFO "systime synchronization at $curtime"

export ros_master="localhost"
export xavier_type="single"        #??~Uxavier or ¡Á?~Lxavier
export ros_machine="${ros_master}" #?¡Â?¡èo:rosmaster ?¡°N?¡èo:rosslave

ethnet_ip=$(ifconfig | grep -v "inet6" | grep -Eo '192[.]168([.][0-9]+){2}' | grep -v "255")
if [ -z "$ethnet_ip" ]; then
        LoggingERR "ip address is null"
        exit 1
fi
ros_machine=$(grep -E "$ethnet_ip.*ros.*" /etc/hosts | grep -v "^#" | uniq | head -1 | awk '{print $2}')
if [ -z "$ros_machine" ]; then
        xavier_type="single"
        ros_machine="titan-ubuntu1"
        ros_master=$ros_machine
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

set_bashrc
LoggingINFO "rosmachine:${ros_machine} rosmaster:${ros_master} xavier_type:${xavier_type}"

source /opt/ros/melodic/setup.bash
source /home/mogo/catkin_ws/devel/setup.bash
source /home/mogo/.bashrc

while true
do
	check_pid
	sleep 1
done
