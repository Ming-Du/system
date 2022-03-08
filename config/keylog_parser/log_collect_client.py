import os
import socket
import time

work_dir = "/home/mogo/data/log"
#work_dir = "/tmp/keylog_parser"
src_dir = os.path.join(work_dir, "ROS_STAT", "EXPORT")
tmp_dir = os.path.join(work_dir, "ROS_STAT_TMP")

# scp -l Kb/s
def run_once():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连不上会抛异常
    try:
        sock.connect(('rosslave', 1119))
    except Exception as e:
        return

    # 先截取一遍文件
    files = os.listdir(src_dir)
    for file_name in files:
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

    while True:
        start = time.time()
        run_once()
        end = time.time()

        sleep_time = 1 - (end - start)
        if sleep_time > 0.3:
            time.sleep(sleep_time)

def main():
    #return run()
    while True:
        pid = os.fork()
        if pid == 0:
            run()
        else:
            os.waitpid(pid, 0)
            print("child exit, rerun")
            time.sleep(1)

if __name__ == '__main__':
    main()


