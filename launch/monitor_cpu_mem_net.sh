#!/bin/bash

TOTAL_TIME=$((60 * 60 * 24)) # 设置脚本运行总时间。单位：秒
INTERVAL=1
NUM=$((${TOTAL_TIME} / ${INTERVAL}))
NEED_PKGS=('iftop')
PYTHON3_MODELS=("psutil")
HOSTSFILE=/etc/hosts
ROS="ros"
THE_NODE_IP=$(ifconfig eth0 | grep "inet 192.168" | awk '{print $2}')
DATE_TIME=$(date "+%Y-%m-%d")
LOGFILE="/home/mogo/data/log/monitor_cpu_mem_net/${DATE_TIME}/"

python3_model_check() {
  if python3 -c "import $1" >/dev/null 2>&1; then
    echo "1"
  else
    echo "0"
  fi
}

function check_package() {
  pkg_miss=()
  for pkg in ${NEED_PKGS[*]}; do
    if [ ! "$(command -v $pkg)" ]; then
      pkg_miss+=(${pkg})
    fi
  done
  if [ ${#pkg_miss[*]} -gt 0 ]; then
    apt-get update
  fi
  for p in ${pkg_miss[*]}; do
    apt-get install $p -y >/dev/null 2>&1
  done
}

function Get_Host_Ips() {
  cat $HOSTSFILE | while read LINE; do
    if [[ $LINE =~ $ROS ]]; then         # 包含$ROS的行
      array=($(echo $LINE | tr ',' ' ')) # 将字符串分割成数组（1）
      echo ${array[0]}
    fi
  done
}

function main() {
  check_package

  # 判断日志目录是否存在，不存在创建目录
  if [ ! -d ${LOGFILE} ]; then
    mkdir -p ${LOGFILE}
  fi
  ip_array=$(Get_Host_Ips)
  for ip in ${ip_array[*]}; do
    if [ $ip != $THE_NODE_IP ]; then
      log_file="${LOGFILE}ping_${ip}.log"
      ping -D -c ${NUM} -i ${INTERVAL} ${ip} >>${log_file} 2>&1 &
    fi
  done
  for model in ${PYTHON3_MODELS[*]}; do
    model_result=$(python3_model_check $model)
    if [ $model_result == 1 ]; then
      echo "OK"
    else
      pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple $model
    fi
  done
}

main
python3 /home/mogo/autopilot/share/launch/monitor_cpu_mem_net.py >/dev/null 2>&1 &
