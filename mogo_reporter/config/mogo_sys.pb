error
{
  code: EHW_LIDAR
  msg: "未检测到雷达"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_HARDWARE_ENGINEER"
}

error
{
  code: EHW_GNSS
  msg: "未检测到gnss"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_CONTACT_HARDWARE_ENGINEER"
}

error
{
  code: EHW_RTK
  msg: "定位不准，gnss节点反馈的状态不是42"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_HARDWARE_ENGINEER"
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
  code: EMAP_NODE
  msg: "节点异常退出"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EMAP_NODE_DEAD
  msg: "节点异常退出过多，放弃重启"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_TECH_SUPPORT"
  action: "ACTION_REBOOT_VEHICLE"
}

error
{
  code: EMAP_HADMAP_ENGINE_NO_ROUTING_INFO
  msg: "hadmap_engine算路失败或未找到轨迹文件导致的轨迹文件信息未发布"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EMAP_EXIT_AUTOPILOT_FOR_DISTANCE
  msg: "因planning起点距离当前过远强退自动驾驶"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EMAP_HADMAP_NO_TRAJECTORY
  msg: "hadmap未发布全局路径"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EMAP_HADMAP_PLANNING_NO_TRAJECTORY
  msg: "local_planning未发布局部轨迹"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EMAP_CONTROL_ABNORMAL_COMMAND
  msg: "controller发布的控制指令异常"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EMAP_CAN_ADAPTER_NO_CHASSIS_INFO
  msg: "can_adapter未成功转发地盘信息"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_REBOOT_VEHICLE"
}

error
{
  code: EVHC_CSS
  msg: "底盘不允许进入自动驾驶"
  result: "RESULT_AUTOPILOT_DISABLE"
  result: "RESULT_REMOTEPILOT_DISABLE"
  action: "ACTION_REBOOT_VEHICLE"
  action: "ACTION_REPAIR_VEHICLE"
}



















