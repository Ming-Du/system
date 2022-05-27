#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import socket
import time

work_dir = "/home/mogo/data/log"
#work_dir = "/tmp/keylog_parser"
src_dir = os.path.join(work_dir, "msg_log")
tmp_dir = os.path.join(work_dir, "msg_log_temp")

# scp -l Kb/s
def run_once():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连不上会抛异常
    try:
        sock.connect(('rosslave', 1120))
    except Exception as e:
        try:
            sock.connect(('rosslave-103', 1120))
        except Exception as e:
            return 
    # 先截取一遍文件
    files = os.listdir(src_dir)
    for file_name in files:
        if file_name in ("autopilot_report.json", "mogodoctor_report.json", "system_master_report.json"):
            file_path = os.path.join(src_dir, file_name)
            tmp_file_path = os.path.join(tmp_dir, file_name)

            os.rename(file_path, tmp_file_path)

    # 将截取数据发出去
    files = os.listdir(tmp_dir)
    for file_name in files:
        tmp_file_path = os.path.join(tmp_dir, file_name)
        with open(tmp_file_path, "rb") as fp:
            sock.sendfile(fp)

    sock.close()

    os.system("rm -f {0}/*".format(tmp_dir))

def run():
    if os.path.exists(tmp_dir) == False:
        os.mkdir(tmp_dir)
    if os.path.exists(src_dir) == False:
        os.mkdir(src_dir)

    while True:
        start = time.time()
        run_once()
        end = time.time()

        sleep_time = 1 - (end - start)
        if sleep_time > 0.3:
            time.sleep(sleep_time)

def main():
    run()
if __name__ == '__main__':
    main()


