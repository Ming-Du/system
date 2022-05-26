error
{
  code: EMAP_EXIT_AUTOPILOT_FOR_PLANNING
  msg: "因planning掉帧强退自动驾驶"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EMAP_EXIT_AUTOPILOT_FOR_LOCATION
  msg: "因location掉帧强退自动驾驶"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EMAP_EXIT_AUTOPILOT_FOR_CHASSIS
  msg: "因底盘消息掉帧强退自动驾驶"
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
