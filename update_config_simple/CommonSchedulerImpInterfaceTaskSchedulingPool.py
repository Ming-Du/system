#!/usr/bin/env python
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

globalThreadExecutePool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='globalThreadExecutePool')


## collect zombile process
def signal_handler(signum, frame):
    try:
        rospy.logdebug("recv signal:{0}".format(signum))
        pid, exit_status = os.waitpid(0, os.WNOHANG)
        rospy.logdebug("sub pid:{0},status:{1}".format(pid, exit_status))
        if exit_status == 0:
            rospy.logdebug("normal  exit")
        if exit_status != 0:
            rospy.logdebug("abnormal  exit")
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


class CommonSchedulerImpInterfaceTaskSchedulingPool(InterfaceTaskSchedulingPool):
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
        # signal.signal(signal.SIGCHLD, signal_handler)
        self.setThreadPool(globalThreadExecutePool)
        pass

    def destroy_module(self):
        pass

    def register_executor(self, ):
        self.mExecutor = Executor()
        pass

    def add_task(self,refDataSource, refJob):
        try:
            curSec = rospy.rostime.Time.now().secs
            curNsec = rospy.rostime.Time.now().nsecs
            CurrentMicroSec = curSec * 1000 + curNsec / 1000000
            refJob[0].intJobCtime = CurrentMicroSec
            while True:
                if refJob[0].enumJobType == EnumJobType.JOB_TYPE_DELAY:
                    self.mDictDelay[refJob[0].intJobCtime] = refJob[0]
                    break
                if refJob[0].enumJobType == EnumJobType.JOB_TYPE_IMMEDIATELY:
                    self.mDictImmediately[refJob[0].intJobCtime] = refJob[0]
                    break
                break
            rospy.loginfo("add_job_to_queue ,self.mDictDelay:{0},self.mDictImmediately:{1}".format(self.mDictDelay,                                                                          self.mDictImmediately))
            self.scheduler_again()
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def add_job_to_queue(self, refDataSource, refJob):
        rospy.loginfo("============ scheduler recv task from queue")
        self.mThreadPool.submit(self.add_task, refDataSource, refJob)

    def action_autopilot_status_change(self, intPilotMode):
        try:
            while True:
                if int(intPilotMode) == -1:
                    break
                if int(intPilotMode) == 0:
                    break
                if int(intPilotMode) == 1:
                    break
                if int(intPilotMode) == 2:
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def changeJobStatus(self, instanceJob):
        pass

    def getTaskFromTable(self):
        instanceJob = None
        enumJobTableType = None
        try:
            instanceJob = None
            intSelectTaskKeyFromImmediately = 0
            intSelectTaskKeyFromDelay = 0
            enumJobTableType = EnumJobType.JOB_TYPE_INIT
            rospy.logdebug("----------------getTaskFromTable -------------self.mDictImmediately:{0},self.mDictDelay:{1}".format(
                self.mDictImmediately, self.mDictDelay))

            ## select use DictImmediately or
            while True:
                listKey = []
                # select   DictImmediately_jobs  or DictDelay_job
                if len(self.mDictImmediately) > 0:
                    for key in self.mDictImmediately.keys():
                        rospy.logdebug("key:{0}".format(int(key)))
                        listKey.append(int(key))
                    listKey.sort()
                    if len(listKey) > 0:
                        rospy.logdebug("get key from mDictImmediately task")
                        intSelectTaskKeyFromImmediately = listKey[len(listKey) - 1]
                        enumJobTableType = EnumJobType.EnumJobType.JOB_TYPE_IMMEDIATELY
                    break
                # mDictDelay jobs select
                if len(self.mDictDelay) > 0:
                    for key in self.mDictDelay.keys():
                        rospy.logdebug("key:{0}".format(int(key)))
                        listKey.append(int(key))
                    listKey.sort()
                    if len(listKey) > 0:
                        rospy.logdebug("get key from mDictDelay task")
                        intSelectTaskKeyFromDelay = listKey[0]
                        enumJobTableType = EnumJobType.JOB_TYPE_DELAY
                    break
                break

            while True:
                if intSelectTaskKeyFromImmediately > 0:
                    instanceJob = self.mDictImmediately[intSelectTaskKeyFromImmediately]
                    break
                if intSelectTaskKeyFromDelay > 0:
                    instanceJob = self.mDictDelay[intSelectTaskKeyFromDelay]
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return instanceJob, enumJobTableType

    def scheduler_again(self):
        rospy.loginfo("---active scheduler_again------")
        try:
            # compare
            # get current Executor_job
            instanceJob, enumJobTableType = self.getTaskFromTable()
            rospy.logdebug("####### ++++ instanceJob:{0},enumJobTableType:{1}".format(instanceJob, enumJobTableType))
            currentExecutorRunningJob = self.mExecutor.getCurrentExecutorRunningJob()
            rospy.logdebug("******* currentExecutorRunningJob:{0}".format(currentExecutorRunningJob))
            while True:
                if enumJobTableType == EnumJobType.JOB_TYPE_IMMEDIATELY:
                    ## compare
                    if instanceJob is None:
                        rospy.logdebug("&&&&&&&&&&&&&& IMMEDIATELY  instanceJob is None")
                        break
                    if currentExecutorRunningJob is None:
                        rospy.logdebug("&&&&&&&&  IMMEDIATELY currentExecutorRunningJob is None")
                        self.mDictImmediately[instanceJob.intJobCtime] = instanceJob
                        self.mDictImmediately[instanceJob.intJobCtime].enumStatus = EnumJobStatus.JOB_STATUS_RUNNING
                        self.mExecutor.run_executor_job(instanceJob)
                        break
                    if (instanceJob is not None) and (currentExecutorRunningJob is not None) and (
                            instanceJob.intJobCtime > currentExecutorRunningJob.intJobCtime):
                        # start replace current job
                        # parse current task and fix status
                        self.mDictImmediately[
                            currentExecutorRunningJob.intJobCtime].enumStatus = EnumJobStatus.JOB_STATUS_PAUSE
                        self.mExecutor.stop_current_executor_job()
                        # start new task and fix status
                        self.mDictImmediately[instanceJob.intJobCtime] = instanceJob
                        self.mDictImmediately[instanceJob.intJobCtime].enumStatus = EnumJobStatus.JOB_STATUS_RUNNING
                        self.mExecutor.run_executor_job(instanceJob)
                        rospy.logdebug("--------------------------------------end finish down load")
                        instanceJob.handlerDataSource.schedulerFinishAction(instanceJob)
                    else:
                        pass
                    break
                if enumJobTableType == EnumJobType.JOB_TYPE_DELAY:
                    if instanceJob is None:
                        rospy.logdebug("&&&&&&&&&&&&&& DELAY instanceJob is None")
                        break
                    if currentExecutorRunningJob is None:
                        rospy.logdebug("&&&&&&&&  DELAY currentExecutorRunningJob is None")
                        self.mDictDelay[instanceJob.intJobCtime] = instanceJob
                        self.mDictDelay[instanceJob.intJobCtime].enumStatus = EnumJobStatus.JOB_STATUS_RUNNING
                        self.mExecutor.run_executor_job(instanceJob)
                        rospy.logdebug("--------------------------------------end finish down load")
                        instanceJob.handlerDataSource.schedulerFinishAction(instanceJob)
                        break
                    if (instanceJob is not None) and (currentExecutorRunningJob is not None) and (
                            instanceJob.intJobCtime < currentExecutorRunningJob.intJobCtime):
                        # start replace current job
                        # parse current task and fix status
                        self.mDictDelay[
                            currentExecutorRunningJob.intJobCtime].enumStatus = EnumJobStatus.JOB_STATUS_PAUSE
                        self.mExecutor.stop_current_executor_job()
                        # start new task and fix status
                        self.mDictDelay[instanceJob.intJobCtime] = instanceJob
                        self.mDictDelay[instanceJob.intJobCtime].enumStatus = EnumJobStatus.JOB_STATUS_RUNNING
                        self.mExecutor.run_executor_job(instanceJob)
                        rospy.logdebug("--------------------------------------end finish down load")
                        instanceJob.handlerDataSource.schedulerFinishAction(instanceJob)
                    else:
                        pass
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
