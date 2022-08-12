info {
  code: IMAP_TRA_EXIST
  msg: "已找到轨迹文件"
}

info {
  code: IMAP_TRA_ROUTING
  msg: "算路成功"
}

info {
  code: IMAP_DATA_EXIST
  msg: "加载正确的sqlite"
}

info {
  code: IMAP_TRA_TYPE
  msg: "加载轨迹类型通知"
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
  code: EMAP_DATA_NOT_EXIST
  msg: "无法加载到正确的sqlite文件"
  result: "RESULT_AUTOPILOT_DISABLE"
  action: "ACTION_CONTACT_TECH_SUPPORT"
}
