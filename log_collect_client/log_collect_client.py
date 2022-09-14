#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import socket
import time
import datetime

work_dir = "/home/mogo/data/log"
src_dir = os.path.join(work_dir, "ROS_STAT", "EXPORT")
tmp_dir = os.path.join(work_dir, "ROS_STAT_TMP")
bak_dir = os.path.join(work_dir, "ROS_STAT", '{}'.format(datetime.date.today()))
once_save_fd = open(bak_dir+"/local_bak_{}".format(int(time.time())), 'ab+')

# scp -l Kb/s
def run_once():
    global once_save_fd
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连不上会抛异常
    try:
        sock.connect(('rosslave', 1119))
    except Exception as e:
        try:
            sock.connect(('rosslave-103', 1119))
        except Exception as e:
            print('sock connect error, {}'.format(e))
            sock.close()
            return
            
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
    files.sort()  # 每秒写文件需要排序发送
    for file_name in files:
        tmp_file_path = os.path.join(tmp_dir, file_name)
        with open(tmp_file_path, "rb") as fp:
            sock.sendfile(fp)
            # 280开始零散文件合并备份保存，5秒备份一次
            # os.sendfile(once_save_fd, fp, 0, 10000)
            once_save_fd.write(fp.read()) 
         
        #bak_file_path = os.path.join(bak_dir, file_name)
        #os.rename(tmp_file_path, bak_file_path)

    sock.close()
    os.system("rm -f {0}/*".format(tmp_dir))

def run():
    global once_save_fd
    while True:
        start = time.time()
        try:
            once_save_fd = open(bak_dir+"/local_bak_{}".format(int(start)), 'ab+')
            run_once()
            once_save_fd.close()
        except Exception as e:
            print("[{}] have error: {}".format(time.time(), e))
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


