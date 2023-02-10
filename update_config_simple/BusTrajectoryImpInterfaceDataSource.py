#!/usr/bin/env python
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d]' '- %(levelname)s: %(message)s',
                    level=logging.INFO)
logging.debug('debug message')
import os
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor
import common.message_pad_pb2 as common_message_pad_pb2

import rospy

from InterfaceDataSource import InterfaceDataSource
from Job import Job
from JobItem import JobItem
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool

from CacheUtils import CacheUtils
from CommonUtilsReadFile import CommonUtilsReadFile
from CommonPara import CommonPara
from CommonHttpUtils import CommonHttpUtils
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool
from EnumDataSourceType import EnumDataSourceType
from CommonUtilsCompare import CommonUtilsCompare
from EnumJobType import EnumJobType

import std_msgs
from std_msgs.msg import String
from rospy import init_node, Subscriber
import json
from autopilot_msgs.msg import BinaryData
from EnumJobType import EnumJobType
import common.trajectory_agent_sync_status_pb2 as common_trajectory_agent_sync_status_pb2
import common.message_pad_pb2 as common_message_pad_pb2
from  CommonPrivilege import CommonPrivilege
from  CommonPrivilege import EnumPrivilegeCheck

instanceCommonUtils = CommonUtilsCompare()
instanceReadConfigFile = CommonUtilsReadFile()
instanceScheduler = CommonSchedulerImpInterfaceTaskSchedulingPool()
instanceCacheUtils = CacheUtils("/home/mogo/data/trajectory_agent_cache_record.json")

globalProcessRequestPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ProcessRequestPool')

globalPubToSystemMasterStatus = rospy.Publisher("/trajectory_agent/cmd/status", BinaryData, queue_size=1000)


class BusTrajectoryImpInterfaceDataSource(InterfaceDataSource):
    strUrlList = None
    strUrlSync = None
    mScheduler = None
    mEnumDataSourceType = None
    mCacheUtils = None
    mStrConfigFileName = None
    mCommonPara = None
    mInterVal = None
    instanceCommonPrivilege = None

    def __init__(self):
        try:
            self.strUrlList = "https://mdev.zhidaohulian.com/config/file/list"
            self.strUrlSync = "https://mdev.zhidaohulian.com/config/file/sync"
            self.mEnumDataSourceType = EnumDataSourceType.DATA_SOURCE_UPDATE_CONFIG
            self.mStrConfigFileName = "/home/mogo/data/TrajectoryConfigCache.json"
            self.mCommonPara = CommonPara()
            self.mCommonPara.initPara()
            self.mInterVal = 120
            self.instanceCommonPrivilege = CommonPrivilege()
            self.instanceCommonPrivilege.getModuleAllow('hadmap_engine', 'hadmap_engine.launch')
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def setScheduler(self, instanceScheduler):
        try:
            self.mScheduler = instanceScheduler
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def setCacheUtils(self, instanceCacheUtil):
        try:
            self.mCacheUtils = instanceCacheUtil
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def getModuleName(self):
        return "bus_trajectory"

    def getVersion(self):
        pass

    def configure(self):
        intError = 0
        try:
            strConfigFilePath = "/home/mogo/data/TrajectoryConfig.json"
            dictConfig = {}
            intError, dictConfig = instanceReadConfigFile.readJsonConfig(strConfigFilePath)
            if intError == 0 and len(dictConfig) > 0:
                if dictConfig.has_key("url_list"):
                    self.strUrlList = dictConfig['url_list']
                if dictConfig.has_key("url_sync"):
                    self.strUrlSync = dictConfig['url_sync']
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intError

    def init_module(self):
        self.setCacheUtils(instanceCacheUtils)

    def destroy_module(self):
        pass

    def transaction(self, msg):
        try:
            pbLine = common_message_pad_pb2.TrajectoryDownloadReq()
            pbLine.ParseFromString(msg.data)
            # parse pb msg
            lLineId = pbLine.line.lineId
            strTrajUrl = pbLine.line.trajUrl
            rospy.loginfo("type:{0}".format(type(pbLine.line.trajMd5)))
            strTempTrajMd5 = str(pbLine.line.trajMd5)
            strTrajMd5 = strTempTrajMd5
            rospy.loginfo("strTrajMd5:{0}".format(strTrajMd5))
            strStopUrl = pbLine.line.stopUrl
            strTempStopMd5 = str(pbLine.line.stopMd5)
            strStopMd5 = strTempStopMd5
            rospy.logdebug("strStopMd5:{0}".format(strStopMd5))
            timestamp = pbLine.line.timestamp
            strVersion = pbLine.line.vehicleModel
            rospy.loginfo(
                "call_process: recv  lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3},strStopMd5:{4},timestamp:{5},strVersion:{6}".format(
                    lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, strVersion))
            strStandardLocationFileStop = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/JL/stop_{0}.txt".format(
                lLineId)
            strStandardLocationFileTraj = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/JL/traj_{0}.csv".format(
                lLineId)
            downJob = Job()
            listDownJob = []
            # call process File
            jobItemStop = JobItem()
            jobItemStop.strFullFileName = strStandardLocationFileStop
            strFullFileTempName = "{0}.temp".format(jobItemStop.strFullFileName)
            jobItemStop.strFullFileTempName = strFullFileTempName
            jobItemStop.strUrl = strStopUrl
            jobItemStop.strMd5 = strStopMd5
            jobItemStop.intPublishTimeStamp = timestamp

            jobItemTraj = JobItem()
            jobItemTraj.strFullFileName = strStandardLocationFileTraj
            strFullFileTempName = "{0}.temp".format(jobItemTraj.strFullFileName)
            jobItemTraj.strFullFileTempName = strFullFileTempName
            jobItemTraj.strUrl = strTrajUrl
            jobItemTraj.strMd5 = strTrajMd5
            jobItemTraj.intPublishTimeStamp = timestamp

            downJob.listJobCollect.append(jobItemStop)
            downJob.listJobCollect.append(jobItemTraj)
            downJob.handlerDataSource = self
            listDownJob.append(downJob)
            intError = self.getNeedUpdateFile(listDownJob)
            if intError == 0 and len(listDownJob[0].listJobCollectUpdate) > 0:
                self.pushJobScheduler(self, listDownJob)
            if intError == 0 and len(listDownJob[0].listJobCollectUpdate) == 0:
                self.schedulerFinishAction(downJob)




        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def process_topic(self, strTopicName, msg):
        try:
            print "------enter---process_topic: strTopicName:{0} =========".format(strTopicName)
            while True:
                if strTopicName == "/trajectory_agent/cmd/transaction":
                    self.transaction(msg)
                    break
                break
            pass
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def process_cycle(self, dictParameter):
        pass

    def process_startup(self, dictParameter):
        pass

    def getNeedUpdateFile(self, refJob):
        intError = 0
        try:
            if len(refJob) == 0:
                intError = -1
            else:
                instanceCommonUtils.compareJobVersion(refJob, self.mCacheUtils)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intError

    def pushJobScheduler(self, refDataSource, refJob):
        try:
            refJob[0].enumJobType = EnumJobType.JOB_TYPE_IMMEDIATELY
            refJob[0].handlerDataSource = self
            self.mScheduler.add_job_to_queue(refDataSource, refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def schedulerFinishAction(self, refJob):
        try:
            rospy.loginfo("enter BusTrajectoryImpInterfaceDataSource::schedulerFinishAction")
            self.checkAtomicFeature(refJob)
            self.install_stage_path(refJob)
            self.install_dst_path(refJob)
            intResult = self.notify_pad(refJob)
            if intResult == 0:
                self.write_cache_file(refJob)
                rospy.loginfo("intResult == 0, access write cache file")
            else:
                rospy.logwarn("intResult != 0, deny  write cache file")

            self.notify_cloud(refJob)
            self.write_event(refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def checkAtomicFeature(self, refJob):
        rospy.loginfo("enter BusTrajectoryImpInterfaceDataSource::checkAtomicFeature")
        pass

    def install_stage_path(self, refJob):
        rospy.loginfo("enter BusTrajectoryImpInterfaceDataSource::install_stage_path")
        pass

    def install_dst_path(self, refJob):
        try:
            rospy.loginfo("enter BusTrajectoryImpInterfaceDataSource::install_dst_path")
            for idx in range(len(refJob.listJobCollect)):
                if not os.path.exists(refJob.listJobCollect[idx].strFullFileTempName):
                    continue
                shutil.copyfile(refJob.listJobCollect[idx].strFullFileTempName,refJob.listJobCollect[idx].strFullFileName)
                os.remove(refJob.listJobCollect[idx].strFullFileTempName)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_cache_file(self, refJob):
        rospy.loginfo("enter BusTrajectoryImpInterfaceDataSource::write_cache_file")
        try:
            for idx in range(len(refJob.listJobCollect)):
                if not os.path.exists(refJob.listJobCollect[idx].strFullFileName):
                    continue
                intLocalModifyTimeStamp = int(os.path.getmtime(refJob.listJobCollect[idx].strFullFileName))
                strUrl = refJob.listJobCollect[idx].strUrl
                strMd5 = refJob.listJobCollect[idx].strMd5
                intPublishTimestamp = refJob.listJobCollect[idx].intPublishTimeStamp
                self.mCacheUtils.writeFileCacheInfo(refJob.listJobCollect[idx].strFullFileName, strUrl, strMd5, intPublishTimestamp,
                                                    intLocalModifyTimeStamp)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def check_local_files(self, refJob):
        intResultProcess = 1
        try:
            while True:
                if refJob is None:
                    rospy.logwarn("error branch refJob is None")
                    break

                if len(refJob.listJobCollect) < 2:
                    rospy.logwarn("error branch len(refJob.listJobCollect) < 2")
                    intResultProcess = 1
                    break
                if len(refJob.listJobCollect) > 2:
                    rospy.logwarn("error branch len(refJob.listJobCollect) > 2")
                    intResultProcess = 1
                    break
                if os.path.exists(refJob.listJobCollect[0].strFullFileName) and os.path.exists(
                        refJob.listJobCollect[1].strFullFileName):
                    intResultProcess = 2
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intResultProcess

    def notify_pad(self, refJob):
        rospy.loginfo("enter BusTrajectoryImpInterfaceDataSource::notify_pad")
        try:
            pbSend = common_trajectory_agent_sync_status_pb2.TrajectoryAgentSyncStatus()
            pbSend.header.seq = 1
            pbSend.header.stamp.sec = rospy.Time.now().secs
            pbSend.header.stamp.nsec = rospy.Time.now().nsecs
            pbSend.header.frame_id = "trajectory_agent_frame_id"
            pbSend.header.module_name = "trajectory_agent"
            intResultProcess = 1
            intSuccessNum = 0
            for idx in range(len(refJob.listJobCollectUpdate)):
                intTempStatus = -1
                intTempStatus = refJob.listJobCollectUpdate[idx].intStatus
                print "refJob.listJobCollectUpdate[{0}].intStatus:{1}".format(idx, intTempStatus)
                if intTempStatus == 0:
                    intSuccessNum = intSuccessNum + 1

            while True:
                # 2/2 files success , traj and stop  both download success
                if intSuccessNum == 2 and len(refJob.listJobCollectUpdate) == 2:
                    intResultProcess = 0
                    break

                # 1/2 files success
                if intSuccessNum == 1 and len(refJob.listJobCollectUpdate) == 2:
                    intResultProcess = self.check_local_files(refJob)
                    break

                # 0/2 files success
                if intSuccessNum == 0 and len(refJob.listJobCollectUpdate) == 2:
                    # check local files
                    intResultProcess = self.check_local_files(refJob)
                    break

                # 1/1 files success
                if intSuccessNum == 1 and len(refJob.listJobCollectUpdate) == 1:
                    intResultProcess = 0
                    break

                # 0/1 files success
                if intSuccessNum == 0 and len(refJob.listJobCollectUpdate) == 1:
                    intResultProcess = self.check_local_files(refJob)
                    break

                if intSuccessNum == 0 and len(refJob.listJobCollectUpdate) == 0 and len(refJob.listJobCollect) == 2:
                    intResultProcess = 0
                    break

                # local files check
                if intSuccessNum == 0 and len(refJob.listJobCollectUpdate) == 0:
                    intResultProcess = self.check_local_files(refJob)
                    break

                break

            pbSend.sync_status = intResultProcess
            rospy.loginfo("pbSend.sync_status:  {0}".format(intResultProcess))

            strBuffer = pbSend.SerializeToString()
            rosMessage = BinaryData()
            rosMessage.data = strBuffer
            rosMessage.size = len(strBuffer)
            globalPubToSystemMasterStatus.publish(rosMessage)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intResultProcess

    def notify_cloud(self, refJob):
        rospy.loginfo("enter BusTrajectoryImpInterfaceDataSource::notify_cloud")
        pass

    def write_event(self, refJob):
        rospy.loginfo("enter BusTrajectoryImpInterfaceDataSource::write_event")

    def getTimeval(self):
        return self.mInterVal

    def getModulePrivilege(self):
        try:
            pass
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
