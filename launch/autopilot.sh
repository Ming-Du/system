#!/bin/bash
sed -i 's/\(${_CATKIN_SETUP_DIR:=\).*/\1\/home\/mogo\/autopilot}/g' $HOME/autopilot/setup.sh
source $HOME/autopilot/setup.sh

cd $HOME/autopilot/  

source $HOME/autopilot/share/launch/integration.sh
