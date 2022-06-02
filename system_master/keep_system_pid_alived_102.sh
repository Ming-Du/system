#!/bin/bash

check_pid()
{
sysmaster_pid=$(ps -ef | grep "system_master.py" |grep -v grep |awk '{print $2}')
if [ -z "$sysmaster_pid" ]; then
	datetime=$(date +"%Y-%m-%d %H:%M:%S")
	echo "    [$datetime] system_master alread exited, now start again!"
	cd /home/mogo/autopilot/share/system_master/
	nohup python -u system_master.py >> /home/mogo/data/log/system_master.log 2>&1 &
fi
}

while true
do
	check_pid
	sleep 1
done
