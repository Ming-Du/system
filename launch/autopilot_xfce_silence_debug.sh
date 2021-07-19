#!/bin/bash
echo $HOME

script_path=$(readlink -f $0)
ABS_PATH=$(dirname $script_path)
source ${ABS_PATH}/../../../devel/setup.bash
BASHRC="${ABS_PATH}/bashrc_debug.sh"
source ${ABS_PATH}/integration_xfce_silence.sh
