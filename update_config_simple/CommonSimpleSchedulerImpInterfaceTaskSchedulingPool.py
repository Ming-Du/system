#!/usr/bin/env python
import base64
import commands
import json
import subprocess
import sys
import threading
import traceback

import os
import signal
from concurrent.futures import ThreadPoolExecutor

import psutil

from InterfaceTaskSchedulingPool import InterfaceTaskSchedulingPool
from Executor import Executor
from InterfaceDataSource import InterfaceDataSource
from Job import Job
from EnumJobType import EnumJobType
import rospy
from EnumJobStatus import EnumJobStatus
from CommonUtilsCompare import CommonUtilsCompare
import multiprocessing
from ProcessUtil import ProcessUtil

globalSimpleThreadExecutePool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalSimpleThreadExecutePool')
instanceCommonUtilsCompare = CommonUtilsCompare()
dictRunningWgetPid = {}
globalSelectTaskPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalSelectTaskPool')
globalAutopilotStatus = -1
globalSignalCallCallbackPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalSignalCallCallbackPool')
globalRecyleSubProcessPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalRecyleSubProcessPool')

def log_content(strContent):
    strLogFileName = "/home/mogo/data/log/latest/update_config_simple/mainTask.log"
    with open(strLogFileName, "a+") as f:
        f.write(strContent)
        f.write('\n')

def downFileFromUrlWget(strUrl, strTempFileName):
    ret = 0
    status = 0
    global dictRunningWgetPid

    try:
        pid = os.fork()
        while True:
            ##current process wget, abort create process wget
            if len(dictRunningWgetPid) > 0:
                rospy.logdebug("len(dictRunningWgetPid) > 0 ")
                break
            if pid < 0:
                rospy.logdebug("====pid < 0  , create  process failed")
                status = -1
                break
            if pid > 0:
                rospy.logdebug("parent process ")
                dictRunningWgetPid[pid] = 0
                rospy.logdebug("====register sub process_pid:{0}".format(dictRunningWgetPid))
                os.waitpid(pid, 0)
                if dictRunningWgetPid.has_key(pid):
                    del dictRunningWgetPid[pid]
                rospy.logdebug("====after finish wget dictRunningWgetPid:{0}".format(dictRunningWgetPid))
                status = 0
                break
            if pid == 0:
                rospy.logdebug("====sub process")
                os.execl("/usr/bin/wget", "/usr/bin/wget", "-c", "--limit-rate=10M", "--connect-timeout=5",
                         "--dns-timeout=5",
                         "-c", strUrl, "-O", strTempFileName)
                break
            break

        ret = status
    except Exception as e:
        rospy.loginfo('repr(e):{0}'.format(repr(e)))
        rospy.loginfo('e.message:{0}'.format(e.message))
        rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))
        ret = -1
    return ret, strTempFileName


def syncFromCloud(strUrl, strMd5, strTempFileName, MaxTryTimes):
    retNum = 0
    try_times = 0
    if os.path.exists(strTempFileName):
        os.remove(strTempFileName)
    try:
        while True:
            try_times = try_times + 1
            if try_times > MaxTryTimes:
                rospy.logdebug(
                    "Exit  Download  , Download file try times:{0} more than global_MaxTryTimes:{1}".format(try_times,
                                                                                                            MaxTryTimes))
                retNum = -1
                break

            if try_times <= MaxTryTimes:
                retDownload, strTempFileName = downFileFromUrlWget(strUrl, strTempFileName)
                ## download files success
                if retDownload == 0:
                    ## check md5 Success
                    if instanceCommonUtilsCompare.checkFileMd5(strTempFileName) == strMd5:
                        rospy.logdebug("md5 check success:filename:{0}".format(strTempFileName))
                        retNum = 0
                        break
                    ##  check md5 failed
                    if instanceCommonUtilsCompare.checkFileMd5(strTempFileName) != strMd5:
                        rospy.logdebug("md5 check failed:filename:{0}".format(strTempFileName))
                ## download file failed
                if retDownload != 0:
                    rospy.loginfo("Download file failed,try times:{0}".format(try_times))


    except Exception as e:
        rospy.loginfo('repr(e):{0}'.format(repr(e)))
        rospy.loginfo('e.message:{0}'.format(e.message))
        rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))
    return retNum


def downFileFromUrlBase64(strUrl, strTempFileName):
    ret = 0
    data = None

    intErrno = 0
    strBase64Content = ""
    strOriginContent = ""
    content = None
    try:
        strSaveTempFile = "{0}.base64".format(strTempFileName)
        if os.path.exists(strSaveTempFile):
            os.remove(strSaveTempFile)
        ret = downFileFromUrlWget(strUrl, strSaveTempFile)
        while True:
            if os.path.exists(strSaveTempFile):
                with open(strSaveTempFile, 'r') as load_f:
                    content = load_f.read()

                break
            if not os.path.exists(strSaveTempFile):
                break
            break

        dictContent = None
        if len(content) > 0:

            dictContent = json.loads(content)
            if dictContent.has_key('errno'):
                intErrno = int(dictContent['errno'])
                rospy.logdebug(
                    "====================================================================================strUrl:{0},intErrno:{1}".format(
                        strUrl, intErrno))
            if (intErrno == 0) and (dictContent.has_key('result')):
                rospy.logdebug(
                    "-------------------enter  (intErrno == 0) and (dictContent.has_key('result')) and  strTempFileName:{0} ".format(
                        strTempFileName))
                strBase64Content = str(dictContent['result'])

        if len(strBase64Content) > 0:
            strOriginContent = base64.b64decode(strBase64Content)
            rospy.logdebug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ strTempFileName:{0}".format(strTempFileName))
            if os.path.exists(strTempFileName):
                os.remove(strTempFileName)
            with open(strTempFileName, 'ab+') as f:
                f.write(strOriginContent)
    except Exception as e:
        rospy.loginfo('repr(e):{0}'.format(repr(e)))
        rospy.loginfo('e.message:{0}'.format(e.message))
        rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))
        ret = -1
    if os.path.exists(strTempFileName):
        ret = 0
    else:
        ret = -1
    return ret, strTempFileName


def syncFromCloudBase64(strUrl, strMd5, strTempFileName, MaxTryTimes):
    retNum = 0
    try_times = 0
    if os.path.exists(strTempFileName):
        os.remove(strTempFileName)
    try:
        while True:
            try_times = try_times + 1
            if try_times > MaxTryTimes:
                rospy.logdebug(
                    "Exit  Download  , Download file try times:{0} more than global_MaxTryTimes:{1}".format(try_times,
                                                                                                            MaxTryTimes))
                retNum = -1
                break

            if try_times <= MaxTryTimes:
                retDownload, strTempFileName = downFileFromUrlBase64(strUrl, strTempFileName)
                ## download files success
                if retDownload == 0:
                    ## check md5 Success
                    if instanceCommonUtilsCompare.checkFileMd5(strTempFileName) == strMd5:
                        rospy.logdebug("md5 check success:filename:{0}".format(strTempFileName))
                        retNum = 0
                        break
                    ##  check md5 failed
                    if instanceCommonUtilsCompare.checkFileMd5(strTempFileName) != strMd5:
                        rospy.logdebug("md5 check failed:filename:{0}".format(strTempFileName))
                ## download file failed
                if retDownload != 0:
                    rospy.loginfo("Download file failed,try times:{0}".format(try_times))

    except Exception as e:
        rospy.loginfo('repr(e):{0}'.format(repr(e)))
        rospy.loginfo('e.message:{0}'.format(e.message))
        rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))
    return retNum


def func_task_select(instanceScheduler, intPilotStatus):
    listNotExistsPid = []
    intSelectRunningPid = -1
    try:
        instanceScheduler.mLockDictRunningJob.acquire()
        if intPilotStatus == 0:
            # push  delay  and imediatly
            listImmediately = []
            listDelay = []
            for k, v in instanceScheduler.mDictRunningJob.items():
                cTimeItem = k
                jobItem = v
                while True:
                    if jobItem.enumJobType == EnumJobType.JOB_TYPE_IMMEDIATELY:
                        listImmediately.append(cTimeItem)
                        break
                    if jobItem.enumJobType == EnumJobType.JOB_TYPE_DELAY:
                        listDelay.append(cTimeItem)
                        break
                    break

            listImmediately.sort()
            listDelay.sort()
            intIdxImmediately = -1
            intIdxDelay = -1
            jobInfoSelect = Job()
            # select runing pid
            while True:
                if len(listImmediately) > 0:
                    intIdxImmediately = listImmediately[len(listImmediately) - 1]

                    break
                if len(listDelay) > 0:
                    intIdxDelay = listDelay[0]

                    break
                break
            intSelectRunningPid = -1

            while True:
                if intIdxImmediately > -1:
                    jobInfoSelect = instanceScheduler.mDictRunningJob[intIdxImmediately]
                    intSelectRunningPid = jobInfoSelect.intPid
                    break
                if intIdxDelay > -1:
                    jobInfoSelect = instanceScheduler.mDictRunningJob[intIdxDelay]
                    intSelectRunningPid = jobInfoSelect.intPid
                    break
                break
            log_content("intSelectRunningPid:{0}".format(intSelectRunningPid))
            if intSelectRunningPid > -1:
                # process status alived, only scheduler alived process
                pHandler = ProcessUtil(intSelectRunningPid)
                intExists,strStatus = pHandler.getProcessStatus()
                ## process exist and not zombile
                if intExists == 1 and strStatus != "zombie":
                    os.kill(intSelectRunningPid, signal.SIGUSR2)
                    log_content("signal CONT  kill -SIGUSR2 {0}".format(intSelectRunningPid))
                else:
                    log_content("pid :{0} not  exists".format(intSelectRunningPid))

        # stop task
        for k, v in instanceScheduler.mDictRunningJob.items():
            jobCTimeItem = k
            jobItem = v
            pHandler = ProcessUtil(v.intPid)
            intExists, strStatus = pHandler.getProcessStatus()
            ## process exist and not zombile
            if intExists == 1 and strStatus != "zombie":
                # stop task except  intSelectRunningPid
                log_content("signal STOP intSelectRunningPid:{0},jobItem.intPid:{1}".format(intSelectRunningPid, jobItem.intPid))
                if jobItem.intPid != intSelectRunningPid:
                    os.kill(jobItem.intPid, signal.SIGUSR1)
                    log_content("signal STOP kill -SIGUSR1 {0}".format(jobItem.intPid))
        #clear failed pid
        if intSelectRunningPid > -1:
            pHandler = ProcessUtil(intSelectRunningPid)
            intExists, strStatus = pHandler.getProcessStatus()
            deleteKey1 = None
            deleteKey2 = None
            if intExists == 0:
                for k, v in instanceScheduler.mDictRunningJob.items():
                    if v.intPid == intSelectRunningPid:
                        deleteKey1 = k
                        deleteKey2 = intSelectRunningPid
                del instanceScheduler.mDictRunningJob[deleteKey1]
                del instanceScheduler.mDictRunningJobRevert[deleteKey2]

    except Exception as e:
        print('repr(e):{0}'.format(repr(e)))
        print('e.message:{0}'.format(e.message))
        print('traceback.format_exc():%s' % (traceback.format_exc()))
    finally:
        instanceScheduler.mLockDictRunningJob.release()




class CommonSimpleSchedulerImpInterfaceTaskSchedulingPool(InterfaceTaskSchedulingPool):
    mExecutor = None
    mDictDelay = None
    mDictImmediately = None
    mThreadPool = None
    mLockDictRunningJob = None
    mDictRunningJob = None
    mDictRunningJobRevert = None
    mTaskSelectPool = None
    mSignalCallbackPool = None

    def __init__(self):
        self.mDictDelay = {}
        self.mDictImmediately = {}
        self.register_executor()
        self.mLockDictRunningJob = threading.RLock()
        self.mDictRunningJob = {}
        self.mDictRunningJobRevert = {}
        self.mSignalCallbackPool = globalSignalCallCallbackPool

    def getModuleName(self):
        pass

    def getVersion(self):
        pass

    def setThreadPool(self, instanceThreadPool, instanceSelectPool):
        self.mThreadPool = instanceThreadPool
        self.mTaskSelectPool = instanceSelectPool

    def configure(self):
        pass

    def init_module(self):
        self.setThreadPool(globalSimpleThreadExecutePool, globalSelectTaskPool)
        pass

    def destroy_module(self):
        pass

    def register_executor(self):
        self.mExecutor = Executor()
        pass


    def add_task(self, refDataSource, refJob):
        processInfo = None
        try:
            intParentPid = os.getpid()
            intPid = -1
            if refJob is not None and len(refJob) > 0:
                print("add_task-----refJob[0].listJobCollect:{0},listJobCollectUpdate:{1},type:{2}".format(
                    len(refJob[0].listJobCollect), len(refJob[0].listJobCollectUpdate),
                    type(refJob[0].handlerDataSource)))
                strModuleName = refJob[0].handlerDataSource.getModuleName()
                curSec = rospy.rostime.Time.now().secs
                curNsec = rospy.rostime.Time.now().nsecs
                refJob[0].intJobCtime = curSec * 1000000000 + curNsec
                strJobFeature = "{0}_{1}".format(strModuleName, refJob[0].intJobCtime)
                refJob[0].mStrJobFeature = strJobFeature

                strTaskFileName = refJob[0].strTaskListFile
                if os.path.exists(strTaskFileName):
                    rospy.logwarn("reject create process ,return")
                    return
                else:
                    rospy.logwarn("===============   fork ")
                intLenList = self.runPriorityExecutorJobGenWgetConfig(refJob[0])
                rospy.loginfo("refJob[0].strDownTempFolder:{0}".format(refJob[0].strDownTempFolder))
                from  SubTask import main as sub_main
                processInfo = multiprocessing.Process(target=sub_main,
                                                      args=(strTaskFileName,))
                processInfo.start()
                refJob[0].intPid = int(processInfo.pid)
                rospy.loginfo(
                    "===============  parent_pid:{0},create sub_pid:{1},type:{2}".format(os.getpid(), refJob[0].intPid,
                                                                                         type(processInfo.pid)))
                self.mLockDictRunningJob.acquire()
                self.mDictRunningJob[refJob[0].intJobCtime] = refJob[0]
                self.mDictRunningJobRevert[refJob[0].intPid] = refJob[0]
        except Exception as e:
            print('repr(e):{0}'.format(repr(e)))
            print('e.message:{0}'.format(e.message))
            print('traceback.format_exc():%s' % (traceback.format_exc()))

        finally:
            self.mLockDictRunningJob.release()
        self.mTaskSelectPool.submit(func_task_select, self, globalAutopilotStatus)
        rospy.loginfo("-------add_task----task process finished--------------")

    def add_job_to_queue(self, refDataSource, refJob):
        rospy.logdebug("add_job_to_queue refJob:{0}".format(refJob))
        if refJob is not None and len(refJob) > 0:
            print("============ scheduler recv task from queue")
            rospy.loginfo("add_job_to_queue-----refJob[0].listJobCollect:{0},listJobCollectUpdate:{1},type:{2}".format(
                len(refJob[0].listJobCollect), len(refJob[0].listJobCollectUpdate), type(refJob[0].handlerDataSource)))
            self.mThreadPool.submit(self.add_task, refDataSource, refJob)

    def action_autopilot_status_change(self, intPilotMode):
        rospy.loginfo_throttle(1, "action_autopilot_status_change recv mode:{0}".format(intPilotMode))
        global globalAutopilotStatus
        try:
            if globalAutopilotStatus != intPilotMode:
                rospy.logwarn("change driver mode to:{0}".format(intPilotMode))
                globalAutopilotStatus = intPilotMode
                func_task_select(self, globalAutopilotStatus)
        except Exception as e:
            rospy.loginfo('repr(e):{0}'.format(repr(e)))
            rospy.loginfo('e.message:{0}'.format(e.message))
            rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))

    def changeJobStatus(self, instanceJob):
        pass

    def getTaskFromTable(self):
        pass


    def run_executor_job(self, instanceJob):
        MaxTryTimes = 5
        rospy.loginfo("---------------run_executor_job active------------------")
        try:
            intCurrentJobId = instanceJob.strJobId
            rospy.loginfo("##########   intCurrentJobId:{0}".format(intCurrentJobId))
            self.mJob = instanceJob
            listTemp = instanceJob.listJobCollectUpdate
            rospy.loginfo("############# run_executor_job: listTemp:{0}".format(listTemp))
            for idx in range(len(instanceJob.listJobCollectUpdate)):
                if len(instanceJob.listJobCollectUpdate[idx].strFullFileTempName) > 0:
                    strFolderName = os.path.dirname(instanceJob.listJobCollectUpdate[idx].strFullFileTempName)
                    rospy.logdebug("================== strFolderName:{0}".format(strFolderName))
                    if os.path.exists(strFolderName):
                        pass
                    else:
                        os.makedirs(strFolderName)
                        os.chmod(strFolderName, 0777)
                    if os.path.exists(instanceJob.listJobCollectUpdate[idx].strFullFileTempName):
                        os.remove(instanceJob.listJobCollectUpdate[idx].strFullFileTempName)
                    intDownStatus = syncFromCloud(instanceJob.listJobCollectUpdate[idx].strUrl,
                                                  instanceJob.listJobCollectUpdate[idx].strMd5,
                                                  instanceJob.listJobCollectUpdate[idx].strFullFileTempName,
                                                  MaxTryTimes)
                    rospy.loginfo("=====intDownStatus:{0}".format(intDownStatus))
                    instanceJob.listJobCollectUpdate[idx].intStatus = intDownStatus
                else:
                    rospy.loginfo("------------------------ ignore: {0}".format(listTemp[idx].strFullFileTempName))
            if len(instanceJob.listJobCollectUpdate) > 0:
                instanceJob.handlerDataSource.schedulerFinishAction(instanceJob)
            else:
                rospy.loginfo("enter func run_executor_job len(instanceJob.listJobCollectUpdate) branch")
                instanceJob.handlerDataSource.relink()
        except Exception as e:
            rospy.loginfo('repr(e):{0}'.format(repr(e)))
            rospy.loginfo('e.message:{0}'.format(e.message))
            rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))

    def run_block_executor_job(self, instanceJob):
        MaxTryTimes = 5
        rospy.loginfo("---------------run_executor_job active------------------")
        try:
            intCurrentJobId = instanceJob.strJobId
            rospy.loginfo("##########   intCurrentJobId:{0}".format(intCurrentJobId))
            self.mJob = instanceJob
            listTemp = instanceJob.listJobCollectUpdate
            rospy.loginfo("############# run_executor_job: listTemp:{0}".format(listTemp))
            for idx in range(len(instanceJob.listJobCollectUpdate)):
                if len(instanceJob.listJobCollectUpdate[idx].strFullFileTempName) > 0:
                    strFolderName = os.path.dirname(instanceJob.listJobCollectUpdate[idx].strFullFileTempName)
                    rospy.logdebug("================== strFolderName:{0}".format(strFolderName))
                    if os.path.exists(strFolderName):
                        pass
                    else:
                        os.makedirs(strFolderName)
                        os.chmod(strFolderName, 0777)
                    if os.path.exists(instanceJob.listJobCollectUpdate[idx].strFullFileTempName):
                        os.remove(instanceJob.listJobCollectUpdate[idx].strFullFileTempName)

                    intDownStatus = self.syncBlockFromCloud(instanceJob.listJobCollectUpdate[idx].strUrl,
                                                            instanceJob.listJobCollectUpdate[idx].strMd5,
                                                            instanceJob.listJobCollectUpdate[idx].strFullFileTempName,
                                                            MaxTryTimes)
                    rospy.loginfo("=====intDownStatus:{0}".format(intDownStatus))
                    instanceJob.listJobCollectUpdate[idx].intStatus = intDownStatus
                else:
                    rospy.loginfo("------------------------ ignore: {0}".format(listTemp[idx].strFullFileTempName))
            if len(instanceJob.listJobCollectUpdate) > 0:
                instanceJob.handlerDataSource.schedulerFinishAction(instanceJob)
            else:
                rospy.loginfo("len(instanceJob.listJobCollectUpdate) == 0,enter install_dst_path")
                instanceJob.handlerDataSource.relink()
        except Exception as e:
            rospy.loginfo('repr(e):{0}'.format(repr(e)))
            rospy.loginfo('e.message:{0}'.format(e.message))
            rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))

    def syncBlockFromCloud(self, strUrl, strMd5, strTempFileName, MaxTryTimes):
        retNum = 0
        try_times = 0
        if os.path.exists(strTempFileName):
            os.remove(strTempFileName)
        try:
            while True:
                try_times = try_times + 1
                if try_times > MaxTryTimes:
                    rospy.logdebug(
                        "Exit  Download  , Download file try times:{0} more than global_MaxTryTimes:{1}".format(
                            try_times,
                            MaxTryTimes))
                    retNum = -1
                    break

                if try_times <= MaxTryTimes:
                    strCmd = "/usr/bin/wget  --connect-timeout=5 --dns-timeout=5  {0} -O {1}".format(strUrl,
                                                                                                     strTempFileName)
                    retDownload, strOutput = commands.getstatusoutput(strCmd)
                    rospy.loginfo("wget strCmd:{0}".format(strCmd))
                    if retDownload == 0:
                        if instanceCommonUtilsCompare.checkFileMd5(strTempFileName) == strMd5:
                            rospy.logdebug("md5 check success:filename:{0}".format(strTempFileName))
                            retNum = 0
                            break
                        if instanceCommonUtilsCompare.checkFileMd5(strTempFileName) != strMd5:
                            rospy.logdebug("md5 check failed:filename:{0}".format(strTempFileName))
                    if retDownload != 0:
                        rospy.loginfo("Download file failed,try times:{0}".format(try_times))


        except Exception as e:
            rospy.loginfo('repr(e):{0}'.format(repr(e)))
            rospy.loginfo('e.message:{0}'.format(e.message))
            rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))
        return retNum

    def run_executor_job_base64(self, instanceJob):
        MaxTryTimes = 5
        rospy.loginfo("-------------enter func run_executor_job_base64-----------------")
        try:
            intCurrentJobId = instanceJob.strJobId
            rospy.loginfo("##########   intCurrentJobId:{0}".format(intCurrentJobId))
            self.mJob = instanceJob
            listTemp = instanceJob.listJobCollectUpdate
            for idx in range(len(instanceJob.listJobCollectUpdate)):
                if len(instanceJob.listJobCollectUpdate[idx].strFullFileTempName) > 0:
                    strFolderName = os.path.dirname(instanceJob.listJobCollectUpdate[idx].strFullFileTempName)
                    rospy.logdebug("================== strFolderName:{0}".format(strFolderName))
                    if os.path.exists(strFolderName):
                        pass
                    else:
                        os.makedirs(strFolderName)
                        os.chmod(strFolderName, 0777)
                    if os.path.exists(instanceJob.listJobCollectUpdate[idx].strFullFileTempName):
                        os.remove(instanceJob.listJobCollectUpdate[idx].strFullFileTempName)
                    intDownStatus = syncFromCloudBase64(instanceJob.listJobCollectUpdate[idx].strUrl,
                                                        instanceJob.listJobCollectUpdate[idx].strMd5,
                                                        instanceJob.listJobCollectUpdate[idx].strFullFileTempName,
                                                        MaxTryTimes)
                    rospy.loginfo("=====intDownStatus:{0}".format(intDownStatus))
                    instanceJob.listJobCollectUpdate[idx].intStatus = intDownStatus
                else:
                    rospy.loginfo("------------------------ ignore: {0}".format(listTemp[idx].strFullFileTempName))
            if len(instanceJob.listJobCollectUpdate) > 0:
                instanceJob.handlerDataSource.schedulerFinishAction(instanceJob)
            else:
                rospy.loginfo("enter func run_executor_job_base64  len(instanceJob.listJobCollectUpdate) branch")
                instanceJob.handlerDataSource.relink()
        except Exception as e:
            rospy.loginfo('repr(e):{0}'.format(repr(e)))
            rospy.loginfo('e.message:{0}'.format(e.message))
            rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))

    def runPriorityExecutorJobGenWgetConfig(self, instanceJob):
        listStrFileName = []
        dictFileLogRecord = {}
        MaxTryTimes = 5
        dictContent = {}
        listObject = []
        rospy.loginfo("---------------run_executor_job active------------------")
        try:
            intCurrentJobId = instanceJob.strJobId
            rospy.loginfo("##########   intCurrentJobId:{0}".format(intCurrentJobId))
            self.mJob = instanceJob
            listTemp = instanceJob.listJobCollectUpdate
            rospy.loginfo("############# run_executor_job: listTemp:{0}".format(listTemp))
            strTaskFileName = "{0}".format(instanceJob.strTaskListFile)
            for idx in range(len(instanceJob.listJobCollectUpdate)):
                if len(instanceJob.listJobCollectUpdate[idx].strFullFileTempName) > 0:
                    strFolderName = os.path.dirname(instanceJob.listJobCollectUpdate[idx].strFullFileTempName)
                    rospy.logdebug("================== strFolderName:{0}".format(strFolderName))
                    if os.path.exists(strFolderName):
                        pass
                    else:
                        os.makedirs(strFolderName)
                        os.chmod(strFolderName, 0777)
                    if os.path.exists(instanceJob.listJobCollectUpdate[idx].strFullFileTempName):
                        os.remove(instanceJob.listJobCollectUpdate[idx].strFullFileTempName)

                    url = instanceJob.listJobCollectUpdate[idx].strUrl
                    dictObject = {}
                    dictObject['url'] = url
                    dictObject['obj_name'] = instanceJob.listJobCollectUpdate[idx].strFullFileTempName
                    listObject.append(dictObject)
            dictContent['data'] = listObject
            with open(strTaskFileName, "a+") as f:
                strJsonContent = json.dumps(dictContent)
                f.write(strJsonContent)
                f.write("\n")
        except Exception as e:
            rospy.loginfo('repr(e):{0}'.format(repr(e)))
            rospy.loginfo('e.message:{0}'.format(e.message))
            rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))
        return len(listStrFileName)


    def wait_pid_no_block(self):
        listClearAlreadyRecycledPid = []
        listClearAlreadyRecycledCtime = []
        intSelectPid = -1
        intSelectStatus = -1
        pid = -1
        exit_status = -1
        try:
            self.mLockDictRunningJob.acquire()
            if len(self.mDictRunningJob) > 0:
                for k, v in self.mDictRunningJob.items():
                    # while true branch
                    # case 1 already recycled pid, should remove from task_list
                    # case 2 alived pid,  should  ingore
                    # case 3 zombile pid, should  process, call signalProcess
                    while True:
                        # ignore pid ,process already recycle by parent process
                        pHandleProcess = ProcessUtil(v.intPid)
                        intExists,strProcessStatus = pHandleProcess.getProcessStatus()
                        if intExists == 0:
                            listClearAlreadyRecycledPid.append(v.intPid)
                            listClearAlreadyRecycledCtime.append(k)
                            break
                        # process pid zombile status
                        # zombiled  feature  file /proc/{pid} exists and file /proc/{pid}/exe not exists
                        if intExists == 1 and strProcessStatus == "zombie":
                            pid, exit_status = os.waitpid(v.intPid, os.WNOHANG)
                            if pid > 0 and exit_status == 0:
                                print "ok,child process over,pid:{0},status:{1}".format(v.intPid, exit_status)
                                intSelectPid = v.intPid
                                intSelectStatus = exit_status
                                if v.intPid == pid:
                                    instanceJob = v
                                    instanceJob.handlerDataSource.schedulerFinishAction(instanceJob)
                                    strTaskFileName = instanceJob.strTaskListFile
                                    if os.path.exists(strTaskFileName):
                                        os.remove(strTaskFileName)
                                    intExist , strStatus = pHandleProcess.getProcessStatus()
                                    if intExist == 0:
                                        listClearAlreadyRecycledPid.append(v.intPid)
                                        listClearAlreadyRecycledCtime.append(k)

                            break
                        break

                for idx in range(len(listClearAlreadyRecycledPid)):
                    intPid = listClearAlreadyRecycledPid[idx]
                    intCtime = listClearAlreadyRecycledCtime[idx]
                    if self.mDictRunningJob.has_key(intCtime):
                        del self.mDictRunningJob[intCtime]
                    if self.mDictRunningJobRevert.has_key(intPid):
                        del self.mDictRunningJobRevert[intPid]
                func_task_select(self, globalAutopilotStatus)
        except Exception as e:
            print('repr(e):{0}'.format(repr(e)))
            print('e.message:{0}'.format(e.message))
            print('traceback.format_exc():%s' % (traceback.format_exc()))
        finally:
            self.mLockDictRunningJob.release()

    def RecycleSubProcess(self):
        try:
            globalRecyleSubProcessPool.submit(self.wait_pid_no_block)
        except Exception as e:
            rospy.loginfo('repr(e):{0}'.format(repr(e)))
            rospy.loginfo('e.message:{0}'.format(e.message))
            rospy.loginfo('traceback.format_exc():%s' % (traceback.format_exc()))
