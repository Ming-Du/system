info {
  code: IMAP_TRA_EXIST
  msg: "已找到轨迹文件"
}

info {
  code: IMAP_TRA_LOADED
  msg: "轨迹文件加载成功"
}

error
{
  code: EMAP_TRA_NOT_EXIST
  msg: "无法找到轨迹文件"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}

error
{
  code: EMAP_TRA_LOAD_FAILED
  msg: "加载轨迹文件失败"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}