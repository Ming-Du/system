info {
  code: ISYS_STARTING
  msg: "系统启动中"
}

info {
  code: ISYS_RUNNING
  msg: "所有Xavier启动完成"
}

info {
  code: ISYS_EXITING
  msg: "系统退出中"
}

info {
  code: ISYS_AUTOPILOT_READY
  msg: "自动驾驶状态就绪"
}

info {
  code: ISYS_AUTOPILOT_STARTING	
  msg: "自动驾驶启动中"
}

info {
  code: ISYS_AUTOPILOT_RUNING
  msg: "自动驾驶运行中"
}

info {
  code: ISYS_TOPIC_FREQ_NORMAL
  msg: "topic频率正常或者恢复正常"
}

info {
  code: ISYS_CAN_NORMAL
  msg: "底盘状态正常或恢复正常"
}

info {
  code: ISYS_REOMTEPILOT_STARTING
  msg: "平行驾驶启动中"
}

info {
  code: ISYS_REOMTEPILOT_RUNING
  msg: "平行驾驶运行中"
}

info {
  code: ILCT_RTK_STATUS_NORMAL
  msg: "rtk状态正常或恢复正常"
}

info {
  code: ISYS_INIT_TRAJECTORY_START
  msg: "轨迹管理_轨迹开始下载"
}

info {
  code: ISYS_INIT_TRAJECTORY_TIMEOUT
  msg: "轨迹管理_轨迹下载超时"
}

info {
  code: ISYS_INIT_TRAJECTORY_SUCCESS
  msg: "轨迹管理_轨迹下载成功"
}

info {
  code: ISYS_INIT_TRAJECTORY_FAILURE
  msg: "轨迹管理_轨迹下载失败，本地无对应轨迹"
}

info {
  code: ISYS_INIT_TRAJECTORY_WARNING
  msg: "轨迹管理_轨迹下载失败，本地有对应轨迹，认为成功"
}

error
{
  code: ESYS_AUTOPILOT_FAILED
  msg: "在尝试启动自动驾驶，但是超过指定时间后底盘未进入，会发送此事件"
  result: "RESULT_AUTOPILOT_INFERIOR"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_TRY_AGAIN_LATER"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: ESYS_IN_INIT
  msg: "系统处于启动中，拒绝进入自动驾驶/远程驾驶"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_TRY_AGAIN_LATER"
}

error
{
  code: ESYS_IN_EXIT
  msg: "系统处于退出中，拒绝进入自动驾驶/远程驾驶"
  result: "RESULT_AUTOPILOT_DISABLE"
}

error
{
  code: ESYS_NOT_ALLOW_AUTOPILOT_FOR_REMOTE
  msg: "系统处于远程驾驶中，拒绝进入自动驾驶"
  result: "RESULT_AUTOPILOT_DISABLE"
}

error
{
  code: ESYS_NOT_ALLOW_REBOOT
  msg: "重启拒绝"
  action: "ACTION_TRY_AGAIN_LATER"
}

error
{
  code: ESYS_TOPIC_FREQ_DROPED
  msg: "存在topic严重掉频"
  result: "RESULT_AUTOPILOT_INFERIOR"
}

error
{
  code: ESYS_AUTOPILOT_TAKEN_OVER_BY_REMOTE
  msg: "自动驾驶被远程驾驶接管"
  result: "RESULT_AUTOPILOT_DISABLE"
}

error
{
  code: EHW_CAN
  msg: "无法与底盘通信，获取不到地盘状态，无法进入自动驾驶"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_REBOOT_VEHICLE"
}

error
{
  code: ESYS_ROUTING_REQ_TIMEOUT
  msg: "自动驾驶开始前，routing请求无响应"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_TRY_AGAIN_LATER"
}

error
{
  code: ESYS_FAULT
  msg: "master启动10分钟，仍有agent未连接"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_REBOOT_VEHICLE"
}

error
{
  code: ELCT_RTK_STATUS_FAULT
  msg: "RTK状态错误"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: ELCT_RTK_STATUS_UNKNOWN
  msg: "RTK状态不确定"
  result: "RESULT_SHOW_WARNING"
}





