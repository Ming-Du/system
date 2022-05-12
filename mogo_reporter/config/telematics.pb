info {
  code: ITELEMATICS_ROUTING_REQUEST_SENT
  msg: "已发送算路请求"
}

info {
  code: ITELEMATICS_AUTOPILOT_CMD_FORWARDED
  msg: "自动驾驶命令已转发"
}

info {
  code: ITELEMATICS_AICLOUD_AUTH_OK	 
  msg: "aicloud连接认证成功"
}

error
{
  code: ETELEMATICS_AICLOUD_AUTH_ERROR
  msg: "telematics连接云端失败"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EVHC_GEAR
  msg: "档位不是D或N档"
  result: "RESULT_AUTOPILOT_DISABLE"
  result: "RESULT_REMOTEPILOT_DISABLE"
  action: "ACTION_HANDLE_VEHICLE_TURN_GEAR"
  action: "ACTION_TRY_AGAIN_LATER"
}









