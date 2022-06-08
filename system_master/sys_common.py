#!/usr/bin/python2 
# -*- coding: utf-8 -*-
'''
Author: your name
Date: 2022-04-27 15:30:24
LastEditTime: 2022-05-12 09:22:32
LastEditors: liyuelei liyuelei@zhidaoauto.com
Description: the file used for common api or method
FilePath: /catkin_ws/src/system/system_master/sys_common.py
'''

import sys 
import trace 
import threading 
import time 
import subprocess
import pexpect


# Python program using traces to kill threads 
class thread_with_trace(threading.Thread): 
    '''
    copy from network used trace kill thread
    '''
    def __init__(self, *args, **keywords): 
        threading.Thread.__init__(self, *args, **keywords) 
        self.killed = False
    def start(self): 
        self.__run_backup = self.run 
        self.run = self.__run	 
        threading.Thread.start(self) 
    def __run(self): 
        sys.settrace(self.globaltrace) #精髓在这里，但我还没有理解为什么要这么做。。。
        self.__run_backup() 
        self.run = self.__run_backup 
    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
            return self.localtrace 
        else: 
            return None
    def localtrace(self, frame, event, arg): 
        if self.killed: 
            if event == 'line': 
                raise SystemExit() 
        return self.localtrace 
    def kill(self): 
        self.killed = True
 

def execute_cmd(cmd, timeout=5):
    """
    Execute command used subprocess, if message times out, return none.

    :param cmd: type of string.
    :param timeout: default is 5.
    :return:    status: 0 is normal, others is abnormal
                result: type of string/None.
    """
    res_err_flag = 0
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    start_time = time.time()
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - start_time
        # 超过timeout时间直接上报
        if timeout and seconds_passed > timeout:
            print('[ERROR][CMD]\tNo response in %d sec! Please check the MCH!', seconds_passed)
            print('[WARN][CMD]\tTimeout while send: %s', cmd)
            p.stdout.flush()
            p.terminate()
            res_err_flag = -1
        time.sleep(0.1)
    if res_err_flag == 0:
        result = p.stdout.read()
        status = p.stdout.close()
        if status is None:
            status = 0
    else:
        status = p.stdout.close()
        if status is None:
            status = 0
        result = None
    return status, result

def ssh_command (password, cmd):
    ssh_newkey = 'Are you sure you want to continue connecting'
    conn_fail = 'Connection failed'
    conn_refused = 'Connection refused'
    # no_route = 'No route to host'    
    # key_error = 'Host key verification failed' 
    passwd_error = 'Permission denied, please try again.'
    child = pexpect.spawn(cmd)
    child.timeout = 10
    i = child.expect([pexpect.TIMEOUT, ssh_newkey, conn_fail, conn_refused, 'password: ', pexpect.exceptions.EOF])
     
    # 如果登录超时，打印出错信息，并退出.
    if i == 0: # Timeout
        msg = 'Run command [%s] ERROR! Please check network' % cmd
        # print (child.before, child.after)
        return -1, msg
 
    # 如果 ssh 没有 public key，接受它.
    if i == 1: # SSH does not have the public key. Just accept it.
        child.sendline ('yes')
        i = child.expect([pexpect.TIMEOUT, 'password: '])
        if i == 0: # Timeout
            msg = 'Send yes ERROR! SSH could not login.'
            # print (child.before, child.after)
            return -2, msg
 
    if i == 2 or i == 3:
        msg = 'Connect ERROR! Please check network or config'
        return -3, msg
    if i == 4: 
        child.sendline(password)
        i = child.expect([pexpect.TIMEOUT, pexpect.EOF, pexpect.exceptions.TIMEOUT, pexpect.exceptions.EOF, passwd_error])
        # print (i,'*'*17,'\n',child.before)
        if i == 4:
            msg = 'SSH Passwd ERROR! Please check the password input'
            return -4, msg
 
    msg = child.before
    if i != 2 and i != 3:
        time.sleep(2)    
    
    child.close()
    return 0, msg

'''

def get_thread_id():
    """
 
    Get PID of thread.
    :return: type of int, return PID of thread.
 
    """
    ## 186(32 bit thread get), 224(64bit thread id get)
    return ctypes.CDLL('libc.so.6').syscall(224)
 
 
def get_os_digits():
    """
 
    Get OS digits, and update the global constants.
    :return: None
 
    """
    os_digits_result = commands.getoutput('uname -m')
    if 'x86_64' in os_digits_result:
        print('OS_DIGITS is 64 bit')
    else:
        print('OS_DIGITS is 32 bit')
 
 
def get_local_mac_address():
    """
 
    Get local MAC address.
    :return: type of string, return local mac address.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_mac_addr = binascii.hexlify(fcntl.ioctl(s.fileno(),
                                                  0x8927,
                                                  struct.pack('64s', config.DEVICE_NETWORK_CARD_NAME))[18:24])
    print('[INFO][DMU]\tDMU local MAC address： {:12s}'.format(
        ':'.join([local_mac_addr[e:e + 2] for e in range(0, 11, 2)])))
    return local_mac_addr
 
 
def get_local_ip_address():
    """
 
    Get local ip address.

    :return: type of string, return local ip address.
 
    """ 
    if not local_ip_addr:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_ip_addr = socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                         0x8915,
                                         struct.pack('256s', config.DEVICE_NETWORK_CARD_NAME))[20: 24])
 
    print('[INFO][DMU]\tDMU local IP address： {:<15s}'.format(local_ip_addr))
    return local_ip_addr
 
 
def get_udp_socket(address):
    """
 
    Get UDP socket.
 
    :param address: type of tuple. (ip address, port)
    :return: return udp socket.
 
    """
   
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(address)
    except Exception as e:
        print("[ERROR] Please check config, socket bind ({},{}) : {} !!".format(address[0], address[1], e))
        sock = None
    return sock
 
 
def get_tcp_socket(address):
    """
 
    Get TCP socket.
 
    :param address: type of tuple. (ip address, port)
    :return: return tcp socket.
 
    """

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(address)
    except Exception as e:
        print("[ERROR] Please check config, socket bind ({},{}) : {} !!".format(address[0], address[1], e))
        sock = None
        if e.args[0] in [98,99]:  # add by liyl 20210406
            print('The Process will exit, because %s', e.args)
            import signal
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            print('The Socket cannot used, because %s', e.args)
    return sock
 
 
def get_sctp_socket(address):
    """
 
    Get SCTP socket.
 
    :param address: type of tuple. (ip address, port)
    :return: return sctp socket.
 
    """
    sock = sctp.sctpsocket_tcp(socket.AF_INET)
    # Allow port multiplexing
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1)
    sock.initparams.max_instreams = 3
    sock.initparams.num_ostreams = 3
    sock.events.clear()
    sock.events.data_io = 1
    sock.bind(address)
    return sock
 
 
def get_mac_socket(address):
    """
 
    Get MAC socket.
 
    :param address: type of tuple. (ip address, port)
    :return: return mac socket.
 
    """
    sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(address[1]))
    sock.bind(address)
    return sock
 
 
def queue_clear(msg_queue):
    """
 
    Clear the queue.
 
    :param msg_queue: type of Queue.
    :return: None.
 
    """
    while not msg_queue.empty():
        msg_queue.get()
 

class NodeThread(threading.Thread):
    def __init__(self, topic, msg_type, call_back, parent=None):
        threading.Thread.__init__(self)
        rospy.Subscriber(topic, msg_type, call_back)
    def run(self):
        rospy.spin()

'''