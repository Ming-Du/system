#!/bin/sh
while :
do
    autopara=`rosparam get /autopilot/PilotMode`
    echo autopara=$autopara
    if [ "$autopara" != "1" ];then
        echo "0" > /home/mogo/autopilot/autopilot_state.txt 
        # echo "now in human"
    else
        echo "1" > /home/mogo/autopilot/autopilot_state.txt 
        # echo "now in auto mode"
    
    fi
    sleep 1
done
