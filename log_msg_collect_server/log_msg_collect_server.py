#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import socket
import time
import threading
import json
import rospy

work_dir = "/home/mogo/data/log"
output_dir = os.path.join(work_dir, "msg_log")
tmp_dir = os.path.join(work_dir, "msg_log_temp")

def recv_data(sock, addr):
    t = time.time()
    index = int(t) % 100000
    filename = "remote_{0}_{1}".format(addr[0], index)
    output_tmp_path = os.path.join(tmp_dir, filename)
    output_path = os.path.join(output_dir, filename)

    empty = True
    with open(output_tmp_path, "ab+") as fp:
        while True:
            contents = sock.recv(1000000)
            # 对端关闭且读完数据，返回''
            if contents == b'':
                break
            fp.write(contents)
            empty = False

    if empty == False:
        os.rename(output_tmp_path, output_path)
    else:
        os.remove(output_tmp_path)


def run():
    if os.path.exists(tmp_dir) == False:
        os.mkdir(tmp_dir)
    if os.path.exists(output_dir) == False:
        os.mkdir(output_dir)
        
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 监听端口:
    s.bind(('0.0.0.0', 1120))
    s.listen(10)
    # print('Waiting for connection...')
    while True:
        # 接受一个新连接:
        sock, addr = s.accept()
        # 创建新线程来处理TCP连接:
        t = threading.Thread(target=recv_data, args=(sock, addr))
        t.start()


""" BEGIN mogo report msg handle """
msg_log_dir = os.path.join(work_dir, "msg_log")
msg_temp_dir = os.path.join(work_dir, "msg_log", "msg_log_temp_handle")
from proto import mogo_report_msg_pb2
from autopilot_msgs.msg import BinaryData

set_msg_log_pub_info = None
set_msg_log_pub_error = None

def PrepareMsgLogPath():
    input_paths = []
    files = os.listdir(msg_log_dir)
    tmp_files = os.listdir(msg_temp_dir)

    for file_name in tmp_files:
        tmp_file_path = os.path.join(msg_temp_dir, file_name)
        input_paths.append(tmp_file_path)

    for file_name in files:
        file_path = os.path.join(msg_log_dir, file_name)
        tmp_file_path = os.path.join(msg_temp_dir, file_name)
        if file_path.find("remote") == -1:
            t = time.time()*1000000
            index = int(t) % 100000
            file_name = "%s_{192.168.0.103}_%d" %(file_name, index) 
        tmp_file_path = os.path.join(msg_temp_dir, file_name)
        os.rename(file_path, tmp_file_path)
        input_paths.append(tmp_file_path)
    return input_paths

def LoadMsglogs(input_paths):
    for path in input_paths:
        try:
            if path.find("swp") == -1:
                LoadOneMsgLog(path)
                os.remove(path)
        except Exception as e:
            print ('loadMsglogs has error: {}'.format(e))

def buildOneLogMsg(one_log_dict):
    #common_mogo_report_msg MogoReportMessage
    mogo_report_msg = mogo_report_msg_pb2.MogoReportMessage()
    try:
        mogo_report_msg.timestamp.sec = one_log_dict["timestamp"]["sec"]
        mogo_report_msg.timestamp.nsec = one_log_dict["timestamp"]["nsec"]
        mogo_report_msg.src = one_log_dict["src"]
        mogo_report_msg.level = one_log_dict["level"]
        mogo_report_msg.msg = one_log_dict["msg"]
        mogo_report_msg.code = one_log_dict["code"]
        if one_log_dict["level"] == "error":
            for result in one_log_dict["result"]:
                mogo_report_msg.result.append(result)
            for action in one_log_dict["actions"]:
                mogo_report_msg.actions.append(action)
        else:
            mogo_report_msg.result.append("")
            mogo_report_msg.actions.append("")

    except Exception as e:
        print ("{} error: {}".format(__name__, e))
    return mogo_report_msg


def LoadOneMsgLog(path):
    try:
        print('path *****', path)
        with open(path) as fp:
            contents = fp.read()
            lines = contents.split("\n")
        for line in lines:
            one_log_dict = {}
            #print("line json is ")
            #print(line)
            one_log_dict = json.loads(line)
            #convert json to protobuf
            log_pub_msg = buildOneLogMsg(one_log_dict)
            log_pub_msg_str = log_pub_msg.SerializeToString()
            binary_log_msg = BinaryData()

            binary_log_msg.header.seq         = 1
            binary_log_msg.header.stamp.secs   = rospy.rostime.Time.now().secs
            binary_log_msg.header.stamp.nsecs  = rospy.rostime.Time.now().nsecs
            binary_log_msg.header.frame_id    = "mogo_msg_handle_frame_id"
            binary_log_msg.name = "mogo_msg_log_handle"
            binary_log_msg.size = len(log_pub_msg_str)
            binary_log_msg.data = log_pub_msg_str
            #print(log_pub_msg_str)
            if one_log_dict["level"] == "info":
                set_msg_log_pub_info.publish(binary_log_msg)
            if one_log_dict["level"] == "error":
                set_msg_log_pub_error.publish(binary_log_msg)

        #mogo_report_msg_test = common_mogo_report_msg.MogoReportMessage()
        #mogo_report_msg_test.ParseFromString(binary_log_msg.data)
        #for one_msg in mogo_report_msg_test.actions:
        #    print(one_msg)
        #for one_msg in mogo_report_msg_test.result:
        #    print(one_msg)
            time.sleep(0.1) # mod by liyl, change 1 to 0.1,  maybe some line after read,  cannot handle
    except Exception as e:
        print ("{} error: {}".format(__name__, e))


def UpdateMsgTopic():
    while(True):
        input_paths=PrepareMsgLogPath()
        if len(input_paths)>0:
            LoadMsglogs(input_paths)
        else:
            time.sleep(1)
        #os.system("rm -f /home/mogo/data/log/msg_log_temp/*")


class MsgLogThread (threading.Thread):
    def __init__(self):
        global set_msg_log_pub_info
        global set_msg_log_pub_error
        rospy.init_node('mogo_msg_log_handle')
        threading.Thread.__init__(self)
        set_msg_log_pub_info  = rospy.Publisher('/autopilot_info/report_msg_info', BinaryData, queue_size=500)
        set_msg_log_pub_error = rospy.Publisher('/autopilot_info/report_msg_error', BinaryData, queue_size=500)
    def run(self):
        if os.path.exists(msg_log_dir) == False:
            os.mkdir(msg_log_dir)
        if os.path.exists(msg_temp_dir) == False:
            os.mkdir(msg_temp_dir)
        
        time.sleep(5)  # wait sub starting
        UpdateMsgTopic()

""" END mogo report msg handle """


def main():
    msg_log_thread = MsgLogThread()
    msg_log_thread.start()
    run()

if __name__ == '__main__':
    main()


