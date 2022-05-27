#!/bin/bash 
# the local file is /home/mogo/autopilot/share/system_master/start_system_master.sh

ethnet_ip=$(ifconfig | grep -v "inet6" | grep -Eo '192[.]168([.][0-9]+){2}' | grep -v "255")
if [ "192.168.1.102" != "$ethnet_ip" ]; then
    echo "ip address not is master, exiting"
    exit 1
fi

LoggingINFO() {
        datetime=$(date +"%Y-%m-%d %H:%M:%S")
        echo -e "\033[32m[ INFO] [$datetime] $*\033[0m"
        [[ -n "$LOGFILE" ]] && echo "[ INFO] [$datetime] $*" >>$LOGFILE
}

install_ros_log() {
        mkdir -p /home/mogo/data/log/msg_log
        chmod 777 -R /home/mogo/data/log/msg_log
}

declare -g LOGFILE
declare -g LOG_DIR="/home/mogo/data/log"
curtime=$(date +"%Y%m%d%H%M%S")
LOGFILE="/home/mogo/data/log/start_master-${curtime}.log"
install_ros_log

export ros_master="localhost"
export ros_machine="${ros_master}"  # 102 must is master

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

set_bashrc
LoggingINFO "rosmachine:${ros_machine} rosmaster:${ros_master}"

source /opt/ros/melodic/setup.bash
source /home/mogo/autopilot/setup.bash
source /home/mogo/.bashrc

start_system_pid=$(ps -ef | grep "keep_system_pid_alived_102.sh" |grep -v grep |awk '{print $2}')
if [ -n "$start_system_pid" ]; then
        kill -9 $start_system_pid
fi
LoggingINFO "first time start"
mv /home/mogo/data/log/system_master.log /home/mogo/data/log/system_master_before.log
rm -f /tmp/system_state

nohup bash /home/mogo/autopilot/share/system_master/keep_system_pid_alived_102.sh >> $LOGFILE 2>&1 &
LoggingINFO "start keep_system_pid_alived success!"
exit 0
