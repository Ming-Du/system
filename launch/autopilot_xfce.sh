#!/bin/bash
sed -i 's/\(${_CATKIN_SETUP_DIR:=\).*/\1\/home\/mogo\/autopilot}/g' /home/mogo/autopilot/setup.sh
source /home/mogo/autopilot/setup.bash

cd /home/mogo/autopilot/  
BASHRC="/home/mogo/autopilot/share/launch/bashrc.sh"
source /home/mogo/autopilot/share/launch/integration_xfce.sh