#!/bin/bash 
# the local file is /home/mogo/autopilot/share/system_master/start_system_master.sh

ethnet_ip=$(ifconfig | grep -v "inet6" | grep -Eo '192[.]168([.][0-9]+){2}' | grep -v "255")
if [ "192.168.1.102" != "$ethnet_ip" ]; then
    echo "ip address not is master, exiting"
    exit 1
fi

start_system_pid=$(ps -ef | grep "keep_system_pid_alived_102.sh" |grep -v grep |awk '{print $2}')
if [ -n "$start_system_pid" ]; then
        kill -9 $start_system_pid
fi
mv /home/mogo/data/log/system_master.log /home/mogo/data/log/system_master_before.log
rm -f /tmp/system_state

nohup bash /home/mogo/autopilot/share/system_master/keep_system_pid_alived_102.sh &
exit 0
