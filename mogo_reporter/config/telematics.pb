info {
  code: ITELEMATICS_AUTOPILOT_CMD_RECEIVED
  msg: "收到自动驾驶命令"
}

info {
  code: ITELEMATICS_AUTOPILOT_CMD_FORWARDED
  msg: "自动驾驶命令已转发"
}

info {
  code: ITELEMATICS_PAD_CONNECTED
  msg: "pad连接已建立"
}

info {
  code: ITELEMATICS_PAD_DISCONNECTED
  msg: "pad连接已断开"
}

info {
  code: ITELEMATICS_AICLOUD_CONNECTED
  msg: "aicloud连接已建立"
}

info {
  code: ITELEMATICS_AICLOUD_AUTH_OK
  msg: "aicloud连接认证成功"
}

info {
  code: ITELEMATICS_AICLOUD_DISCONNECTED
  msg: "aicloud连接已断开"
}

info {
  code: ITELEMATICS_ROUTING_REQUEST_SENT
  msg: "路径规划请求已发送"
}

error
{
  code: ETELEMATICS_START_AUTO_PILOT_FAILED
  msg: "自动驾驶启动失败（没有进行启动自动驾驶命令转发）"
  result: "RESULT_AUTOPILOT_SYSTEM_UNSTARTED"
  action: "ACTION_CHECK_GEAR"
}

error
{
  code: ETELEMATICS_PAD_SEND_ERROR
  msg: "向pad发送失败"
  result: "RESULT_PAD_INFO_LOST"
  action: "ACTION_CHECK_NETWORK"
}

error
{
  code: ETELEMATICS_PAD_RECV_ERROR
  msg: "接收pad失败"
  result: "RESULT_PAD_INFO_LOST"
  action: "ACTION_CHECK_NETWORK"
}

error
{
  code: ETELEMATICS_QUIT
  msg: "telematics进程或者线程退出"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_REBOOT_VEHICLE"
}

error
{
  code: ETELEMATICS_AICLOUD_AUTH_ERROR
  msg: "aicloud认证失败"
  result: "RESULT_NO_CONNECTION_TO_AICLOUD"
  action: "ACTION_CONTACT_MAINTENANCE"
}