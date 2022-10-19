#!/usr/bin/env python
import commands
import traceback

import os
import signal
from concurrent.futures import ThreadPoolExecutor

from InterfaceTaskSchedulingPool import InterfaceTaskSchedulingPool
from Executor import Executor
from InterfaceDataSource import InterfaceDataSource
from Job import Job
from EnumJobType import EnumJobType
import rospy
from EnumJobStatus import EnumJobStatus
from CommonUtilsCompare import CommonUtilsCompare

globalSimpleThreadExecutePool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalSimpleThreadExecutePool')
instanceCommonUtilsCompare = CommonUtilsCompare()
dictRunningWgetPid = {}


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
                os.execl("/usr/bin/wget", "/usr/bin/wget", "--connect-timeout=5", "--dns-timeout=5",
                         "-c", strUrl, "-O", strTempFileName)
                break
            break

        ret = status
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
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
                    rospy.logwarn("Download file failed,try times:{0}".format(try_times))
                # if os.path.exists(strTempFileName):
                #     os.remove(strTempFileName)

    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    return retNum


class CommonSimpleSchedulerImpInterfaceTaskSchedulingPool(InterfaceTaskSchedulingPool):
    mExecutor = None
    mDictDelay = None
    mDictImmediately = None
    mThreadPool = None

    def __init__(self):
        self.mDictDelay = {}
        self.mDictImmediately = {}
        self.register_executor()

    def getModuleName(self):
        pass

    def getVersion(self):
        pass

    def setThreadPool(self, instanceThreadPool):
        self.mThreadPool = instanceThreadPool

    def configure(self):
        pass

    def init_module(self):
        self.setThreadPool(globalSimpleThreadExecutePool)
        pass

    def destroy_module(self):
        pass

    def register_executor(self):
        self.mExecutor = Executor()
        pass

    def add_task(self, refDataSource, refJob):
        try:
            if refJob is not None and len(refJob) > 0:
                rospy.loginfo("add_task-----refJob[0].listJobCollect:{0},listJobCollectUpdate:{1},type:{2}".format(
                    len(refJob[0].listJobCollect), len(refJob[0].listJobCollectUpdate),
                    type(refJob[0].handlerDataSource)))
                self.run_executor_job(refJob[0])



        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        rospy.loginfo("-------add_task----task process finished--------------")

    def add_job_to_queue(self, refDataSource, refJob):
        print("add_job_to_queue refJob:{0}".format(refJob))
        if refJob is not None and len(refJob) > 0:
            rospy.loginfo("============ scheduler recv task from queue")
            rospy.loginfo("add_job_to_queue-----refJob[0].listJobCollect:{0},listJobCollectUpdate:{1},type:{2}".format(
                len(refJob[0].listJobCollect), len(refJob[0].listJobCollectUpdate), type(refJob[0].handlerDataSource)))
            self.mThreadPool.submit(self.add_task, refDataSource, refJob)

    def action_autopilot_status_change(self, intPilotMode):
        rospy.loginfo("action_autopilot_status_change recv mode:{0}".format(intPilotMode))
        try:
            while True:
                if int(intPilotMode) == 0:
                    break
                if int(intPilotMode) == 1:
                    for k, v in dictRunningWgetPid.items():
                        os.kill(k, signal.SIGKILL)
                    break
                if int(intPilotMode) == 2:
                    for k, v in dictRunningWgetPid.items():
                        os.kill(k, signal.SIGKILL)
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def changeJobStatus(self, instanceJob):
        pass

    def getTaskFromTable(self):
        pass

    def scheduler_again(self):
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
                    print "================== strFolderName:{0}".format(strFolderName)
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
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

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
                    print "================== strFolderName:{0}".format(strFolderName)
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
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

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
                    if retDownload == 0:
                        if instanceCommonUtilsCompare.checkFileMd5(strTempFileName) == strMd5:
                            rospy.logdebug("md5 check success:filename:{0}".format(strTempFileName))
                            retNum = 0
                            break
                        if instanceCommonUtilsCompare.checkFileMd5(strTempFileName) != strMd5:
                            rospy.logdebug("md5 check failed:filename:{0}".format(strTempFileName))
                    if retDownload != 0:
                        rospy.logwarn("Download file failed,try times:{0}".format(try_times))


        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return retNum
