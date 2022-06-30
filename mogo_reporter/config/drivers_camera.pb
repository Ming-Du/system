info {
  code: ICAM_READY
  msg: "相机已就绪"
}

error
{
  code: ECAM_INIT
  msg: "相机初始化失败"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: ECAM_CALIB
  msg: "标定信息读取失败"
  result: "RESULT_AUTOPILOT_INFERIOR"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}