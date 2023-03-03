import json
import multiprocessing
import os.path
import signal
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from ProcessUtil import ProcessUtil
import rospy

dictWgetSubPid = {}
globalRecyleSubProcessPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalRecyleSubProcessPool')

def log_content(strContent):
    strLogFileName = "/home/mogo/data/log/latest/update_config_simple/subTask_{0}.log".format(os.getpid())
    with open(strLogFileName, "a+") as f:
        f.write(strContent)
        f.write('\n')

def debug_log_content(strContent):
    strLogFileName = "/home/mogo/data/log/latest/update_config_simple/subTask_{0}_debug.log".format(os.getpid())
    with open(strLogFileName, "a+") as f:
        f.write(strContent)
        f.write('\n')

def sub_process_wget(strUrl, strObjectName):
    try:
        strDestName = strObjectName
        debug_log_content("strDestName:{0}".format(strDestName))
        os.execl("/usr/bin/wget", "/usr/bin/wget", "--limit-rate=100M", "--connect-timeout=5",
                 "--dns-timeout=5", "-t", "20", strUrl, "-O", strDestName)
    except Exception as e:
        debug_log_content('traceback.format_exc():%s' % (traceback.format_exc()))


def wait_pid_no_block():
    global dictWgetSubPid
    listClearAlreadyRecycledPid = []
    intSelectPid = -1
    intSelectStatus = -1
    try:
        if len(dictWgetSubPid) > 0:
            for k, v in dictWgetSubPid.items():
                while True:
                    pHandler = ProcessUtil(k)
                    intExists,strStatus = pHandler.getProcessStatus()
                    # ignore pid ,process already recycle by parent process
                    if intExists == 0:
                        debug_log_content("strPid:{0} not exists,may already recycled, task_list will remove".format(k))
                        listClearAlreadyRecycledPid.append(k)
                        break
                    if intExists == 1 and strStatus == "zombie":
                        pid, exit_status = os.waitpid(k, os.WNOHANG)
                        log_content("os.WEXITSTATUS(exit_status):{0}".format(os.WEXITSTATUS(exit_status)))
                        log_content("os.WTERMSIG(exit_status):{0}".format(os.WTERMSIG(exit_status)))
                        log_content("os.WIFEXITED(exit_status):{0}".format(os.WIFEXITED(exit_status)))
                        log_content("wait_pid_no_block===sub pid:{0},status:{1}".format(pid, exit_status))
                        if pid > 0:
                            log_content("ok,child process over,pid:{0},status:{1}".format(k, exit_status))
                            if 1:
                                intExists, strStatus = pHandler.getProcessStatus()
                                if intExists == 0:
                                    listClearAlreadyRecycledPid.append(k)
                        break
                    break

    except Exception as e:
        debug_log_content('traceback.format_exc():%s' % (traceback.format_exc()))
    finally:
        pass
    debug_log_content("=========== leave wait_pid_no_block=============")


def receive_signal(signum, stack):
    try:
        globalRecyleSubProcessPool.submit(wait_pid_no_block)
    except Exception as e:
        debug_log_content('traceback.format_exc():%s' % (traceback.format_exc()))





def handler_SIGUSR1(signum, frame):
    strLogContent = "recv SIGUSR1"
    log_content(strLogContent)
    # send STOP to sub process
    try:
        for k, v in dictWgetSubPid.items():
            pHandler = ProcessUtil(k)
            intExists,strStatus = pHandler.getProcessStatus()
            if intExists == 1 and strStatus != "zombie":
                if strStatus != "stopped":
                    os.kill(k, signal.SIGSTOP)
                    strLogContent = "siganl stop k:{0}".format(k)
                    log_content(strLogContent)
                else:
                    strLogContent = "signal pid {0} already stopped".format(k)
                    log_content(strLogContent)

    except Exception as e:
        debug_log_content('traceback.format_exc():%s' % (traceback.format_exc()))


def handler_SIGUSR2(signum, frame):
    strLogContent = "recv SIGUSR2"
    log_content(strLogContent)
    try:
        # send CONT to sub process
        for k, v in dictWgetSubPid.items():
            pHandler = ProcessUtil(k)
            intExists, strStatus = pHandler.getProcessStatus()
            if intExists == 1 and strStatus != "zombie":
                if strStatus != "running":
                    os.kill(k, signal.SIGCONT)
                    strLogContent = "siganl cont k:{0}".format(k)
                    log_content(strLogContent)
                else:
                    strLogContent = "signal pid {0} already running".format(k)
                    log_content(strLogContent)

    except Exception as e:
        debug_log_content('traceback.format_exc():%s' % (traceback.format_exc()))


def main(strConfigFile):
    signal.signal(signal.SIGCHLD, receive_signal)
    # send STOP to sub process
    content = "before signal user1"
    log_content(content)
    signal.signal(signal.SIGUSR1, handler_SIGUSR1)
    content = "end signal user1"
    log_content(content)
    # send CONT to subprocess
    content = "before signal user2"
    log_content(content)
    signal.signal(signal.SIGUSR2, handler_SIGUSR2)
    content = "end signal user2"
    log_content(content)
    listJoin = []
    try:
        import sys
        #rospy.logdebug("==============  strConfigFile:{0}".format(strConfigFile))
        strJsonContent = ""
        dictContent = None
        if os.path.exists(strConfigFile):
            with open(strConfigFile, "r") as f:
                strJsonContent = f.read()
            pass
        if len(strJsonContent) > 1:
            dictContent = json.loads(strJsonContent)
            listData = dictContent['data']
            for idx in range(len(listData)):
                debug_log_content("idx:{0},data:{1}".format(idx, listData[idx]))
                strUrl = listData[idx]['url']
                strObjName = listData[idx]['obj_name']
                processInfo = multiprocessing.Process(target=sub_process_wget,
                                                      args=(strUrl, strObjName,))
                listJoin.append(processInfo)
            for idx in range(len(listJoin)):
                listJoin[idx].start()
                dictWgetSubPid[listJoin[idx].pid] = 0
                listJoin[idx].join()
    except Exception as e:
        debug_log_content('traceback.format_exc():%s' % (traceback.format_exc()))

