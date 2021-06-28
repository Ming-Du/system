#!/bin/bash
sed -i 's/\(${_CATKIN_SETUP_DIR:=\).*/\1\/home\/mogo\/autopilot}/g' /home/mogo/autopilot/setup.sh
source /home/mogo/autopilot/setup.bash

cd /home/mogo/autopilot/  

source /home/mogo/autopilot/share/launch/integration.sh
