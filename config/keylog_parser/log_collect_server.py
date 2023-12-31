import os
import socket
import time
import threading

work_dir = "/home/mogo/data/log"
#work_dir = "/tmp/keylog_parser"
output_dir = os.path.join(work_dir, "ROS_STAT", "EXPORT")
tmp_dir = os.path.join(work_dir, "ROS_STAT_REMOTE")

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

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 监听端口:
    s.bind(('0.0.0.0', 1119))
    s.listen(10)
    # print('Waiting for connection...')
    while True:
        # 接受一个新连接:
        sock, addr = s.accept()
        # 创建新线程来处理TCP连接:
        t = threading.Thread(target=recv_data, args=(sock, addr))
        t.start()

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


