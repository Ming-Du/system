#!/bin/bash
echo $HOME

script_path=$(readlink -f $0)
ABS_PATH=$(dirname $script_path)
source /home/mogo/catkin_ws/devel/setup.bash
BASHRC="${ABS_PATH}/../../../bashrc_debug.sh"
source ${ABS_PATH}/integration_xfce.sh
