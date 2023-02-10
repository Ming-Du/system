#!/usr/bin/env python
import os.path
import signal
import traceback

from InterfaceDataSource import InterfaceDataSource
from InterfaceTrigger import InterfaceTrigger
import rospy
# from CommonTriggerImpInterfaceTrigger  import CommonTriggerImpInterfaceTrigger
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool
from InterfaceTaskSchedulingPool import InterfaceTaskSchedulingPool
from InterfaceDataSource import InterfaceDataSource
import threading
from threading import Thread
import schedule
import time


def timer_action_kill_task(pid):
    try:
        os.kill(pid, signal.SIGKILL)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def thread_timer_stop(timeout, pid):
    rospy.loginfo("thread_timer_stop")
    try:
        timer = threading.Timer(timeout, timer_action_kill_task, args=(pid,))
        timer.start()
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


def call_process_cycle(instanceInterfaceDataSource, dictParameter):
    try:
        instanceInterfaceDataSource.process_cycle(dictParameter)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


class CommonTriggerImpInterfaceTrigger(InterfaceTrigger):
    mMapDataSource = None
    mTrigger = None

    def __init__(self):
        self.mMapDataSource = []
        pass

    def getVersion(self):
        pass

    def configure(self):
        pass

    def init_module(self):
        pass

    def destroy(self):
        pass

    def addNotifyDataSourceModule(self, instanceInterfaceDataSource):
        try:
            strModuleIndex = "{0}".format(instanceInterfaceDataSource.getModuleName())
            self.mMapDataSource.append(instanceInterfaceDataSource)
            rospy.loginfo("======= data source add strModuleIndex idx :{0}".format(strModuleIndex))
            rospy.loginfo("======= now self.mMapDataSource:{0}".format(self.mMapDataSource))
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def addNotifyTaskSchedulerPool(self, instanceInterfaceTaskSchedulingPool):
        self.mTrigger = instanceInterfaceTaskSchedulingPool

    def notifyDataSourceModule(self):
        pass

    def notifySchedulerPool(self):
        pass

    def processPilotUpdate(self, intPilotMode):
        try:
            self.mTrigger.action_autopilot_status_change(intPilotMode)
            while True:
                if int(intPilotMode) == -1:
                    break
                if int(intPilotMode) == 0:
                    break
                if int(intPilotMode) == 1:
                    # auto mode
                    break
                if int(intPilotMode) == 2:
                    # parallel  mode
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def processTopicInfo(self, strTopicName, pbTopicInfo):
        rospy.loginfo("#### processTopicInfo---recv from strTopicName:{0}---".format(strTopicName))
        # select handler
        try:
            handler = None
            #strTrajectoryKey = "df_trajectory"
            rospy.logdebug("==processTopicInfo===== now self.mMapDataSource:{0}".format(self.mMapDataSource))
            while True:
                if strTopicName == "/trajectory_agent/cmd/transaction" or strTopicName == "/trajectory_agent/cmd/checktrajstate" :
                    rospy.logdebug("============= self.mMapDataSource:{0}".format(self.mMapDataSource))
                    for idx in range(len(self.mMapDataSource)):
                        if self.mMapDataSource[idx].getModuleName() == "df_trajectory" or self.mMapDataSource[idx].getModuleName() == "bus_trajectory":
                            handler = self.mMapDataSource[idx]
                            rospy.logdebug("====handler:{0}".format(handler))
                            handler.process_topic(strTopicName, pbTopicInfo)
                            break
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def start_loop_internal_timer(self, dictParameter):
        rospy.loginfo("start***** self.mMapDataSource:{0}".format(self.mMapDataSource))
        try:
            for idx in range(0,len(self.mMapDataSource)):
                intTimeVal = self.mMapDataSource[idx].getTimeval()
                schedule.every(intTimeVal).seconds.do(self.mMapDataSource[idx].process_cycle, dictParameter)
            rospy.loginfo("scheduler***** self.mMapDataSource:{0}".format(self.mMapDataSource))
            #schedule.every(10).seconds.do(self.mTrigger.scheduler_again, "")
            while True:
                schedule.run_pending()
                time.sleep(1)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def sub_process(self, dictParameter):
        strFlagEndFile = "/home/mogo/data/config_end"
        if not os.path.exists(strFlagEndFile):
            rospy.loginfo("self.mMapDataSource: {0}".format(self.mMapDataSource))
            try:
                if 1:
                    for idx in range(0, len(self.mMapDataSource)):
                        self.mMapDataSource[idx].process_startup(dictParameter)
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            try:
                strNowTime = time.strftime("%Y-%m-%d %H:%M:%S")
                with open(strFlagEndFile, 'a+') as f:
                    f.write(strNowTime)
                    f.write("\n")
                    f.close()
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            exit(0)

    def process_startup(self, dictParameter):
        self.sub_process(dictParameter)
