info {
  code: IINIT_BOOST
  msg: "linux系统已启动(此事件会延迟发出，timestamp填linux启动时的事件)"
}

info {
  code: IINIT_TIME_SYNC
  msg: "时间已同步"
}

info {
  code: IINIT_SENSOR_NORMAL
  msg: "各传感器正常"
}

info {
  code: IBOOT_MAP_STARTED
  msg: "当前xavier上所有节点已启动成功"
}

info {
  code: IAGENT_EXECUTE_MASTER_COMMAND
  msg: "执行系统指令成功"
}

error
{
  code: EINIT_LOST_FILE
  msg: "系统启动时缺失必要文件，或者容器配置错误"
  result: "RESULT_AUTOPILOT_SYSTEM_UNSTARTED"
  result: "RESULT_AUTOPILOT_DISABLE"
  result: "RESULT_REMOTEPILOT_DISABLE"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EAGENT_FATAL
  msg: "agent严重故障,无法恢复"
  result: "RESULT_AUTOPILOT_DISABLE"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_REBOOT_VEHICLE"
}

error
{
  code: EAGENT_MASTER_COMMAND_HANDLER_FAILED
  msg: "agent未能成功执行master指令"
  action: "ACTION_TRY_AGAIN_LATER"
}



