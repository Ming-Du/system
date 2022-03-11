#!/bin/bash
# candump -n 4 can0 -T 1000
# if [ $? -ne 0 ];then
#     echo "can't start autopilot mode:can error"
#     exit $?
# fi

function checkTopic() {
    local topic=$1
    local key=$2
    echo "" >$topic_tmp_file
    timeout 5 rostopic echo --noarr $topic -n 1 >$topic_tmp_file
    if [ $? -ne 0 ]; then
        echo "$topic has no message"
        return 1
    fi
    if [ ! -z "$key" ]; then
        value=$(cat $topic_tmp_file | grep -w $key | awk -F: '{print $2}')
    fi
    return 0
}

#main
topic_tmp_file="/tmp/topic_tmp.data"
ABS_PATH="$(cd "$(dirname $0)" && pwd)"
CONFIG_PATH="${ABS_PATH}/../config"
if [ "$1" == "c" ]; then
    echo "start to system checking..."
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

    if [ -z "$ROS_HOSTNAME" ]; then
        ROS_HOSTNAME="rosmaster"
    fi
    if [ "$ROS_HOSTNAME" == "rosmaster" ]; then
        #check gnss
        gnss_launch_file="$CONFIG_PATH/vehicle/drivers/gnss/gnss.launch"
        if [ -f $gnss_launch_file ]; then
            gnss_dev=$(xmllint --xpath "//param[@name='device']/@value" $gnss_launch_file 2>/dev/null | awk -F= '{print $2}' | sed 's/ //g' | sed 's/\"//g')
            if [ ! -z "$gnss_dev" ]; then
                echo "checking gnss device:$gnss_dev..."
                if [ ! -e $gnss_dev ]; then
                    echo "$gnss_dev device is abnormal"
                    exit 2
                fi
            else
                echo "gnss device is null"
            fi
            echo "OK"
        fi
        #check lidar
        if [ "$D_CAR_TYPE" == "df" -o "$D_CAR_TYPE" == "hq" ]; then
            device_ip="192.168.1.205"
            echo "checking lidar ip:$device_ip..."
            ping -c 1 -W 2 $device_ip 2>&1 >/dev/null
            if [ $? -ne 0 ]; then
                echo "cannot connect with lidar[$device_ip]"
                exit 3
            fi
            echo "OK"
        elif [ "$D_CAR_TYPE" == "jinlv" ]; then
            lidar_launch_file="$CONFIG_PATH/vehicle/drivers/lidar/lidar.launch"
            for files in $(roslaunch $lidar_launch_file --files); do
                device_ip=$(xmllint --xpath "//arg[@name='device_ip']/@default" $files 2>/dev/null | awk -F= '{print $2}' | sed 's/\"//g')
                [[ -z "$device_ip" ]] && continue
                echo "checking lidar ip:$device_ip..."
                ping -c 1 -W 2 $device_ip 2>&1 >/dev/null
                if [ $? -ne 0 ]; then
                    echo "cannot connect with lidar[$device_ip]"
                    exit 3
                fi
                echo "OK"
            done
        fi
    fi

    #check camera
    camera_launch_file="$CONFIG_PATH/vehicle/drivers/camera/camera.launch"
    for files in $(roslaunch $camera_launch_file --files); do
        dev=$(xmllint --xpath "//arg[@name='video_device']/@default" $files 2>/dev/null | awk -F= '{print $2}' | sed 's/\"//g')
        [[ -z "$dev" ]] && continue
        [[ ! -e $dev ]] && echo "camera device[$dev] is abnormal"
    done
fi

if [ "$1" == "d" ]; then
    #check version
    if [ -f /autocar-code/project_commit.txt ]; then
        sed -n '2p' /autocar-code/project_commit.txt
    else
        echo "no version infomation"
    fi
    #check node
    echo "checking node..."
    for node in $(rosnode list); do
        if [ $(rosnode ping -c 1 $node 2>&1 | grep -wc ERROR) -ne 0 ]; then
            echo "$node has crashed"
        fi
    done

    #check connection
    echo "checking connection with pad..."
    established_conns=$(netstat -nap | grep -w 4110 | grep -cw ESTABLISHED)
    [[ $established_conns -lt 1 ]] && echo "telematics could not connect with Pad"

    echo "checking /autopilot/PilotMode..."
    pilotmode=$(rosparam get /autopilot/PilotMode)
    if [ $? -ne 0 ]; then
        echo "/autopilot/PilotMode has not been set"
        # exit 5
    else
        echo "pilot mode is $pilotmode"
        if [ $pilotmode -eq 1 ]; then
            #check vehicl stat
            echo "checking vehicle chassis pilot mode..."
            checkTopic /vehicle/status/panel "pilot_mode"
            if [ $? -eq 0 ]; then
                [[ $value -eq 0 ]] && echo "autopilot command has been sent,but vehicle couldn't enter into autopilot mode"
            fi
        fi
    fi

    #check gnss stat
    echo "checking gps status..."
    checkTopic /sensor/gnss/gps_fix "  status"
    if [ $? -eq 0 ]; then
        [[ $value -ne 42 ]] && echo "gps status is abnormal:$value"
    fi

    #check /planning/global_trajectory
    checkTopic /planning/global_trajectory

    #check /planning/trajectory
    checkTopic /planning/trajectory
    # if [ $? -ne 0 ]; then
    #     echo "/planning/trajectory has no message"
    #     # exit 5
    # fi
    # /hadmap_engine/lanes_msg [autopilot_msgs/BinaryData]
    # /hadmap_engine/map_convexhull_msg [autopilot_msgs/BinaryData]
    # /hadmap_engine/map_msg [autopilot_msgs/BinaryData]
    # /hadmap_engine/path_info_msg [autopilot_msgs/BinaryData]
    # /rosout [rosgraph_msgs/Log]
fi
