#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import socket
import time
import datetime

work_dir = "/home/mogo/data/log"
src_dir = os.path.join(work_dir, "ROS_STAT", "EXPORT")
tmp_dir = os.path.join(work_dir, "ROS_STAT_TMP")
bak_dir = os.path.join(work_dir, "ROS_STAT", datetime.date.today())

# scp -l Kb/s
def run_once():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连不上会抛异常
    try:
        sock.connect(('rosslave', 1119))
    except Exception as e:
        try:
            sock.connect(('rosslave-103', 1119))
        except Exception as e:
            print('sock connect error, {}'.format(e))
            
    # 先截取一遍文件
    files = os.listdir(src_dir)
    for file_name in files:
        if '.tmp' in file_name:
            # used .tmp match file don't handel
            continue
        file_path = os.path.join(src_dir, file_name)
        tmp_file_path = os.path.join(tmp_dir, file_name)
        os.rename(file_path, tmp_file_path)

    # 将截取数据发出去
    files = os.listdir(tmp_dir)
    for file_name in files:
        tmp_file_path = os.path.join(tmp_dir, file_name)
        with open(tmp_file_path, "rb") as fp:
            sock.sendfile(fp)
        bak_file_path = os.path.join(bak_dir, file_name)
        os.rename(tmp_file_path, bak_file_path)

    sock.close()
    #os.system("rm -f {0}/*".format(tmp_dir))

def run():
    while True:
        start = time.time()
        run_once()
        end = time.time()

        if 1 > end - start:
            time.sleep(1.0 - (end - start))

def main():
    if os.path.exists(tmp_dir) == False:
        os.mkdir(tmp_dir)
    if os.path.exists(src_dir) == False:
        os.makedirs(src_dir) 
    if os.path.exists(bak_dir) == False:
        os.mkdir(bak_dir)

    run()

if __name__ == '__main__':
    main()


