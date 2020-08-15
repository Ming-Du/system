#start chassis driver
gnome-terminal -x bash -c \
  "cd /home/mogo/EMUC-B202 && ./start.sh"

sleep 2
#start ros
gnome-terminal -x bash -c "roscore"
sleep 5
gnome-terminal -x bash -c "rosnode kill -a"

#gnome-terminal -x bash -c "roslaunch telematics telematics.launch"
#gnome-terminal -x bash -c ""
gnome-terminal --window -e "bash -c 'roslaunch telematics telematics.launch';bash" \
  --tab -e "bash -c 'roslaunch /home/mogo/catkin_ws/src/system/launch/drivers.launch';bash" \
  --tab -e "bash -c 'roslaunch /home/mogo/catkin_ws/src/system/launch/perception.launch';bash"

#sleep 2
#gnome-terminal -x bash -c "cd /home/mogo/catkin_ws/src/perception/traffic_sign/ && ./start_sign.sh"
