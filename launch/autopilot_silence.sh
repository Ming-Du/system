#!/bin/bash
sed -i 's/\(${_CATKIN_SETUP_DIR:=\).*/\1\/home\/mogo\/autopilot}/g' $HOME/autopilot/setup.sh
source $HOME/autopilot/setup.bash

cd $HOME/autopilot/  

source $HOME/autopilot/share/launch/integration_silence.sh
