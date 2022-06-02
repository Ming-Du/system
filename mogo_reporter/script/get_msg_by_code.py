import os
import sys
import json
import time
from google.protobuf import text_format
from mogo_report_codes_pb2 import ReportMsgList, ReportMsgCode


def gen_report_msg(pd_name, code):

  path=os.path.dirname(os.path.abspath(__file__))+'/../config/'+os.path.basename(pd_name)
  if not os.path.exists(path):
    print (path)
    return '{}'

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
    cur_time = int(time.time())
    ret["timestamp"] = {
      "sec": cur_time, 
      "nsec": int((time.time() - cur_time) * 1000000000)}, 
    ret["level"] = level
    ret["code"] = ReportMsgCode.Name(msg_tar.code)
    ret["msg"] = msg_tar.msg
    ret["result"] = []
    for it in msg_tar.result:
      ret["result"].append(it)
    ret["action"] = []
    for it in msg_tar.action:
      ret["action"].append(it)
      
  json_str = json.dumps(ret)

  return json_str

if __name__ == '__main__':
  pb_name = sys.argv[1]
  code = sys.argv[2]
  print (gen_report_msg(pb_name, code))
