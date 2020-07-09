#start chassis driver
gnome-terminal -x bash -c "cd /home/mogo/EMUC-B202 && ./start.sh"

sleep 5
#start ros
gnome-terminal -x bash -c "roscore"
sleep 5
gnome-terminal -x bash -c "roslaunch /home/mogo/catkin_ws/src/system/launch/telematics.launch"
sleep 2
gnome-terminal -x bash -c "roslaunch telematics telematics.launch"
#sleep 2
#gnome-terminal -x bash -c "cd /home/mogo/catkin_ws/src/perception/traffic_sign/ && ./start_sign.sh"
