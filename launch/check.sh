#!/bin/bash
# candump -n 4 can0 -T 1000
# if [ $? -ne 0 ];then
#     echo "can't start autopilot mode:can error"
#     exit $?
# fi
if [ "$1" == "c" ]; then
    echo "start to system checking..."
    ABS_PATH="$(cd "$(dirname $0)" && pwd)"
    #check time
    export last_launch_time
    if [ -f $ABS_PATH/launch_time ]; then
        last_launch_time=$(cat $ABS_PATH/launch_time)
    fi
    if [ -z "$last_launch_time" ]; then
        last_launch_time="20211222211202" #随便初始的一个日期时间
    fi
    systime=$(date +"%Y%m%d%H%M%S")
    if [ $systime -gt $last_launch_time ]; then
        echo "systime synchronization at $systime"
        echo $systime >$ABS_PATH/launch_time
    else
        echo "systime is too old"
        exit 1
    fi

    if [ "$ROS_HOSTNAME" == "rosmaster" ]; then
        #check gnss
        if [ ! -e /dev/ttyUSB0 -o ! -e /dev/ttyUSB1 ]; then
            echo "gnss device is abnormal"
            #exit 2
        fi

        #check lidar
        if [ "$D_CAR_TYPE" == "df" -o "$D_CAR_TYPE" == "hq" ]; then
            lidar_ip="192.168.1.205"
        elif [ "$D_CAR_TYPE" == "jinlv" ]; then
            lidar_ip[1]="192.168.8.201"
            lidar_ip[2]="192.168.8.202"
        fi
        for ip in "${lidar_ip[@]}"; do
            ping -c 1 -W 2 $ip
            if [ $? -ne 0 ]; then
                echo "cannot connect with lidar[$ip]"
                #exit 3
            fi
        done
    fi

    #check camera
    for files in $(roslaunch /home/mog/autopilot/share/config/vehicle/drivers/camera/camera.launch --files); do
        dev=$(xmllint --xpath "//arg[@name='video_device']/@default" $files | awk -F= '{print $2}' | sed 's/\"//g')
        [[ -z "$dev" ]] && continue
        [[ ! -e $dev ]] && echo "camera device[$dev] is abnormal"
    done
    exit 0
fi

#check node
if [ "$1" == "d" ]; then
    for disconnected_node in $(rosnode ping -a | grep -B1 ERROR | grep ping | awk '{print $2}'); do
        echo "$disconnected_node has disconnected"
    done

    established_conns=$(netstat -nap | grep -w 4110 | grep -n ESTABLISHED)
    [[ $established_conns -lt 1 ]] && echo "telematics could not connect with Pad" exit 1
    pilotmode=$(rosparam get /autopilot/PilotMode)
    if [ $pilotmode -eq 0 ]; then
        echo "pilot mode is $pilotmode"
    else

    fi
    #check vehicl stat
    vehicle_stat=$(rostopic echo /vehicle/status/panel -n 1 | grep -w pilot_mode | awk '{print $2}')
    [[ $vehicle_stat -eq 0 ]] && echo "autopilot command has been sent,but vehicle couldn't enter into autopilot mode" && exit 3

fi
