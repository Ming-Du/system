import sys
import json
from google.protobuf import text_format
from mogo_report_codes_pb2 import ReportMsgList, ReportMsgCode

path = sys.argv[1] # "/home/kls/workspace/catkin_ws/src/system/mogo_reporter/config/telematics.pb"
code = sys.argv[2] # ITELEMATICS_AUTOPILOT_CMD_RECEIVED

msg_list = ReportMsgList()
with open(path, "r") as fp:
  pd_str = fp.read()
  text_format.Parse(pd_str, msg_list)

ret = {}
level = ""
msg_tar = {}

for msg in msg_list.info:
  if ReportMsgCode.Name(msg.code) == code:
    level = "info"
    msg_tar = msg
    break

if msg_tar == {}:
  for msg in msg_list.error:
    if ReportMsgCode.Name(msg.code) == code:
      level = "error"
      msg_tar = msg
      break

if msg_tar != {}:
  ret["level"] = level
  ret["code"] = ReportMsgCode.Name(msg_tar.code)
  ret["msg"] = msg_tar.msg
  ret["result"] = []
  for it in msg_tar.result:
    ret["result"].append(it)
  ret["action"] = []
  for it in msg_tar.result:
    ret["action"].append(it)
  print(json.dumps(ret))
