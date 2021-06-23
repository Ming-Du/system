#!/bin/bash
sed -i 's/\(${_CATKIN_SETUP_DIR:=\).*/\1\/home\/mogo\/autopilot}/g' $HOME/autopilot/setup.sh
source $HOME/autopilot/setup.bash

cd $HOME/autopilot/  
BASHRC="/home/mogo/autopilot/share/launch/bashrc.sh"
source $HOME/autopilot/share/launch/integration_xfce.sh
