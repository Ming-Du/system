#!/usr/bin/env python
import logging
import threading

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
from TrajV260 import TrajV260
from TrajV250 import TrajV250

instanceCommonUtils = CommonUtilsCompare()
instanceReadConfigFile = CommonUtilsReadFile()
instanceScheduler = CommonSchedulerImpInterfaceTaskSchedulingPool()
instanceCacheUtils = CacheUtils("/home/mogo/data/trajectory_agent_cache_record.json")

globalProcessRequestPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ProcessRequestPool')

globalPubToSystemMasterStatus = rospy.Publisher("/trajectory_agent/cmd/status", BinaryData, queue_size=1000)
from threading import Semaphore
from EnumTrajResult import EnumTrajResult
from EnumTrajResult import TrajResultTranTool
from CommonPrivilege import CommonPrivilege
from CommonPrivilege import EnumPrivilegeCheck
from ConfigUtils import ConfigUtils
instanceConfigUtils = ConfigUtils()


class DfTrajectoryImpInterfaceDataSource(InterfaceDataSource):
    strUrlList = None
    strUrlSync = None
    mScheduler = None
    mEnumDataSourceType = None
    mCacheUtils = None
    mStrConfigFileName = None
    mCommonPara = None
    mInterVal = None
    pTrajHandlerV250 = None
    pTrajHandlerV260 = None
    s_lock = None
    intFirstStatus = None
    instanceCommonPrivilege = None

    def __init__(self):
        try:
            self.mEnumDataSourceType = EnumDataSourceType.DATA_SOURCE_UPDATE_CONFIG
            self.mStrConfigFileName = "/home/mogo/data/TrajectoryConfigCache.json"
            self.mCommonPara = CommonPara()
            self.mCommonPara.initPara()
            self.mInterVal = 120
            self.pTrajHandlerV250 = TrajV250()
            self.pTrajHandlerV260 = TrajV260()
            self.s_lock = threading.Event()
            self.intFirstStatus = -1
            self.instanceCommonPrivilege = CommonPrivilege()
            self.instanceCommonPrivilege.getModuleAllow('hadmap_engine', 'hadmap_engine.launch')


        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def setScheduler(self, instanceScheduler):
        try:
            self.pTrajHandlerV250.setScheduler(instanceScheduler)
            self.pTrajHandlerV260.setScheduler(instanceScheduler)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def setCacheUtils(self, instanceCacheUtil):
        try:
            pass
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def getModuleName(self):
        return "df_trajectory"

    def getVersion(self):
        pass

    def configure(self):
        intError = 0
        try:
            self.pTrajHandlerV250.configure()
            self.pTrajHandlerV250.setCallerHandler(self)
            self.pTrajHandlerV260.configure()
            self.pTrajHandlerV260.setCallerHandler(self)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intError

    def init_module(self):
        self.pTrajHandlerV250.init_module()
        self.pTrajHandlerV260.init_module()
        strConfigFileName = "/autocar-code/install/share/trajectory_agent/traj.conf"
        instanceConfigUtils.initConfig(strConfigFileName)
        instanceConfigUtils.debug()


    def destroy_module(self):
        self.pTrajHandlerV250.destroy_module()
        self.pTrajHandlerV260.destroy_module()

    def transaction(self, msg, strTopicName):
        strDpqpDir = ""
        str250Dir = ""
        while True:
            if self.instanceCommonPrivilege.strCarType == "jinlv":
                strDpqpDir = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/JL/"
                str250Dir = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/JL/"
                break
            if self.instanceCommonPrivilege.strCarType == "df":
                strDpqpDir = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/DF/"
                str250Dir = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/DF/"
                break
            if self.instanceCommonPrivilege.strCarType == "hq":
                strDpqpDir = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/HQ/"
                str250Dir = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/HQ/"
                break
            break
        if not os.path.exists(strDpqpDir):
            os.makedirs(strDpqpDir)
            os.chmod(strDpqpDir,0777)
        if not os.path.exists(str250Dir):
            os.makedirs(str250Dir)
            os.chmod(str250Dir, 0777)

        pbLine = None
        intRet = EnumTrajResult.ENUMTRAJRESULT_V250_SEARCH_LAT_LON_FAILED
        enumTrajValue = EnumTrajResult.ENUMTRAJRESULT_V250_SEARCH_LAT_LON_FAILED
        floatStartX = float(0.0)
        floatStartY = float(0.0)
        floatEndX = float(0.0)
        floatEndY = float(0.0)
        timestamp = 0
        timestampDpqp = 0
        try:
            if msg.size > 0:
                while True:
                    if strTopicName == "/trajectory_agent/cmd/transaction":
                        pbLine = common_message_pad_pb2.TrajectoryDownloadReq()
                        pbLine.ParseFromString(msg.data)
                        break
                    if strTopicName == "/trajectory_agent/cmd/checktrajstate":
                        pbLine = common_trajectory_agent_sync_status_pb2.TrajectoryAgentDownloadCheck()
                        pbLine.ParseFromString(msg.data)
                        floatStartX = float(pbLine.start.x)
                        floatStartY = float(pbLine.start.y)
                        floatEndX = float(pbLine.end.x)
                        floatEndY = float(pbLine.end.y)
                        break
                    break

                lLineId = pbLine.line.lineId
                strTrajUrl = pbLine.line.trajUrl
                strTempTrajMd5 = str(pbLine.line.trajMd5)
                strTrajMd5 = strTempTrajMd5
                strStopUrl = pbLine.line.stopUrl
                strTempStopMd5 = str(pbLine.line.stopMd5)
                strStopMd5 = strTempStopMd5
                timestamp = pbLine.line.timestamp
                if timestamp > 0:
                    timestamp = timestamp / 1000

                strTrajUrlDpqg = pbLine.line.trajUrl_dpqp
                strTrajMd5Dpqp = str(pbLine.line.trajMd5_dpqp)
                strStopUrlDpqp = pbLine.line.stopUrl_dpqp
                strStopMd5Dpqp = str(pbLine.line.stopMd5_dpqp)
                timestampDpqp = pbLine.line.timestamp_dpqp
                if timestampDpqp > 0:
                    timestampDpqp = timestampDpqp / 1000
                rospy.loginfo(
                    "===== recv call_process: recv  lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3},strStopMd5:{4}," \
                    "timestamp:{5},strTrajUrlDpqg:{6},strTrajMd5Dpqp:{7},strStopUrlDpqp:{8},strStopMd5Dpqp:{9}," \
                    "timestampDpqp:{10},floatStartX:{11},floatStartY:{12},floatEndX:{13},floatEndY:{14}".format(
                        lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, strTrajUrlDpqg,
                        strTrajMd5Dpqp,
                        strStopUrlDpqp, strStopMd5Dpqp, timestampDpqp, floatStartX, floatStartY, floatEndX, floatEndY))

                intDistance = instanceConfigUtils.intTraj260Priority - instanceConfigUtils.intTraj250Priority
                while True:
                    # 260 line_id search
                    if (intDistance > 0) and int(lLineId) > 0 and len(strTrajUrlDpqg) > 0 and len(strTrajMd5Dpqp) > 0 and len(
                            strStopUrlDpqp) > 0 and len(strStopMd5Dpqp) > 0 and int(timestampDpqp) > 0:
                        rospy.loginfo("func transaction  user branch pTrajHandlerV260.transaction")
                        self.pTrajHandlerV260.transaction(lLineId, strTrajUrlDpqg, strTrajMd5Dpqp, strStopUrlDpqp,
                                                          strStopMd5Dpqp, timestampDpqp, floatStartX, floatStartY,
                                                          floatEndX, floatEndY)
                        self.block_S()
                        rospy.loginfo(" self.pTrajHandlerV260  intFirstStatus:{0}".format(self.intFirstStatus))
                        if self.intFirstStatus == EnumTrajResult.ENUMTRAJRESULT_V260_TRAJ_WARNING or self.intFirstStatus == EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_SUCCESS or self.intFirstStatus == EnumTrajResult.ENUMTRAJRESULT_V260_SEARCH_LAT_LON_SUCCESS:
                            rospy.logwarn(" transaction match branch ranch pTrajHandlerV260.transaction")
                            enumTrajValue = self.intFirstStatus
                            break
                    # 260 lat_lon traj search
                    if (instanceConfigUtils.intTraj260LonLatTypeEnableFlag == 1) and (intDistance > 0) and int(lLineId) > 0 and len(strTrajUrlDpqg) == 0 and len(strTrajMd5Dpqp) == 0 and len(
                            strStopUrlDpqp) == 0 and len(strStopMd5Dpqp) == 0 and int(timestampDpqp) == 0:
                        rospy.loginfo("func transaction  user branch pTrajHandlerV260.call_para")
                        intRet = self.pTrajHandlerV260.call_para(lLineId, strTrajUrlDpqg, strTrajMd5Dpqp,
                                                                 strStopUrlDpqp, strStopMd5Dpqp, timestampDpqp,
                                                                 floatStartX, floatStartY, floatEndX, floatEndY)
                        if intRet == EnumTrajResult.ENUMTRAJRESULT_V260_TRAJ_WARNING or intRet == EnumTrajResult.ENUMTRAJRESULT_V260_SEARCH_LAT_LON_SUCCESS:
                            rospy.logwarn(" transaction match branch pTrajHandlerV260.call_para")
                            enumTrajValue = intRet
                            break
                    # 250 lat_lon traj search
                    if int(lLineId) > 0 and len(strTrajUrl) > 0 and len(strTrajMd5) > 0 and len(strStopUrl) > 0 and len(
                            strStopMd5) > 0 and int(timestamp) > 0:
                        rospy.loginfo("func transaction  user branch pTrajHandlerV250.transaction")
                        self.pTrajHandlerV250.transaction(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5,
                                                          timestamp, floatStartX, floatStartY, floatEndX, floatEndY)
                        self.block_S()
                        rospy.logwarn(" ==========================================   self.pTrajHandlerV250  intFirstStatus:{0}".format(self.intFirstStatus))
                        if self.intFirstStatus == EnumTrajResult.ENUMTRAJRESULT_V250_TRAJ_WARNING or self.intFirstStatus == EnumTrajResult.ENUMTRAJRESULT_V250_DOWNLOAD_SUCCESS or self.intFirstStatus == EnumTrajResult.ENUMTRAJRESULT_V250_SEARCH_LAT_LON_SUCCESS:
                            rospy.logwarn("transaction match pTrajHandlerV250.transaction")
                            enumTrajValue = self.intFirstStatus
                            break
                    # 250 lat_lon traj search
                    if int(lLineId) > 0 and len(strTrajUrl) == 0 and len(strTrajMd5) == 0 and len(
                            strStopUrl) == 0 and len(strStopMd5) == 0 and int(timestamp) == 0:
                        rospy.loginfo("func transaction  user branch pTrajHandlerV250.call_para")
                        intRet = self.pTrajHandlerV250.call_para(lLineId, strTrajUrl, strTrajMd5, strStopUrl,
                                                                 strStopMd5,
                                                                 timestamp, floatStartX, floatStartY, floatEndX,
                                                                 floatEndY)
                        rospy.loginfo("self.pTrajHandlerV250.call_para after call:{0}".format(intRet))
                        if intRet == EnumTrajResult.ENUMTRAJRESULT_V250_TRAJ_WARNING or intRet == EnumTrajResult.ENUMTRAJRESULT_V250_DOWNLOAD_SUCCESS or intRet == EnumTrajResult.ENUMTRAJRESULT_V250_SEARCH_LAT_LON_SUCCESS:
                            rospy.logwarn("transaction match pTrajHandlerV250.call_para")
                            enumTrajValue = intRet
                            break
                    break
            self.notify_pad(enumTrajValue)
            instJob = Job()
            instJob.setStrJobFeature(self.pTrajHandlerV250.getModuleName(),timestamp)
            if os.path.exists(instJob.strTaskListFile):
                os.remove(instJob.strTaskListFile)
            instJob.setStrJobFeature(self.pTrajHandlerV260.getModuleName(), timestampDpqp)
            if os.path.exists(instJob.strTaskListFile):
                os.remove(instJob.strTaskListFile)


        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def topicMsgCallbackStartup(self, msg):
        try:
            if msg.size > 0:
                pbLine = common_trajectory_agent_sync_status_pb2.TrajectoryAgentDownloadCheck()
                pbLine.ParseFromString(msg.data)
                # parse pb msg
                lLineId = pbLine.line.lineId
                strTrajUrl = pbLine.line.trajUrl
                strTempTrajMd5 = str(pbLine.line.trajMd5)
                strTrajMd5 = strTempTrajMd5
                strStopUrl = pbLine.line.stopUrl
                strTempStopMd5 = str(pbLine.line.stopMd5)
                strStopMd5 = strTempStopMd5
                timestamp = pbLine.line.timestamp

                ## Dpqg  traj
                strTrajUrlDpqg = pbLine.line.trajUrl_dpqp
                strTrajMd5Dpqp = str(pbLine.line.trajMd5_dpqp)
                strStopUrlDpqp = pbLine.line.stopUrl_dpqp
                strStopMd5Dpqp = str(pbLine.line.stopMd5_dpqp)
                timestampDpqp = pbLine.line.timestamp_dpqp

                floatStartX = float(pbLine.start.x)
                floatStartY = float(pbLine.start.y)
                floatEndX = float(pbLine.end.x)
                floatEndY = float(pbLine.end.y)

                rospy.loginfo(
                    "call_process: recv  lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3},strStopMd5:{4}," \
                    "timestamp:{5},strTrajUrlDpqg:{6},strTrajMd5Dpqp:{7},strStopUrlDpqp:{8},strStopMd5Dpqp:{9}," \
                    "timestampDpqp:{10},floatStartX:{11},floatStartY:{12},floatEndX:{13},floatEndY:{14}".format(
                        lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, strTrajUrlDpqg,
                        strTrajMd5Dpqp,
                        strStopUrlDpqp, strStopMd5Dpqp, timestampDpqp, floatStartX, floatStartY, floatEndX, floatEndY))


        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def process_topic(self, strTopicName, msg):
        try:
            rospy.loginfo("------enter---process_topic: strTopicName:{0} =========".format(strTopicName))
            while True:
                if EnumPrivilegeCheck.PRIVILEGE_CHECK_DENY == self.instanceCommonPrivilege.enumPri:
                    rospy.logwarn("DfTrajectoryImpInterfaceDataSource::process_topic PRIVILEGE_CHECK_DENY")
                    break
                if EnumPrivilegeCheck.PRIVILEGE_CHECK_UNKNOW == self.instanceCommonPrivilege.enumPri:
                    rospy.logwarn("DfTrajectoryImpInterfaceDataSource::process_topic PRIVILEGE_CHECK_UNKNOW")
                    break
                if strTopicName == "/trajectory_agent/cmd/transaction":
                    self.transaction(msg, strTopicName)
                    break
                if strTopicName == "/trajectory_agent/cmd/checktrajstate":
                    self.transaction(msg, strTopicName)
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
            pass
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intError

    def pushJobScheduler(self, refDataSource, refJob):
        try:
            pass
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def schedulerFinishAction(self, refJob):
        try:
            rospy.loginfo("enter DfTrajectoryImpInterfaceDataSource::schedulerFinishAction")

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def checkAtomicFeature(self, refJob):
        rospy.loginfo("enter DfTrajectoryImpInterfaceDataSource::checkAtomicFeature")
        pass

    def install_stage_path(self, refJob):
        rospy.loginfo("enter DfTrajectoryImpInterfaceDataSource::install_stage_path")
        pass

    def install_dst_path(self, refJob):
        try:
            rospy.loginfo("enter DfTrajectoryImpInterfaceDataSource::install_dst_path")

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_cache_file(self, refJob):
        rospy.loginfo("enter DfTrajectoryImpInterfaceDataSource::write_cache_file")
        try:
            pass

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def check_local_files(self, refJob):
        intResultProcess = 1
        try:
            pass

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intResultProcess

    def notify_pad(self, trajEnumStatus):
        rospy.loginfo("enter DfTrajectoryImpInterfaceDataSource::notify_pad")
        try:
            pbSend = common_trajectory_agent_sync_status_pb2.TrajectoryAgentSyncStatus()
            pbSend.header.seq = 1
            pbSend.header.stamp.sec = rospy.Time.now().secs
            pbSend.header.stamp.nsec = rospy.Time.now().nsecs
            pbSend.header.frame_id = "trajectory_agent_frame_id"
            pbSend.header.module_name = "trajectory_agent"

            tranTools = TrajResultTranTool()
            intStatus = tranTools.initData(trajEnumStatus)
            pbSend.sync_status = intStatus
            rospy.logwarn("origin pbSend.sync_status:{0}".format(trajEnumStatus))
            rospy.logwarn("========== pb pbSend.sync_status:{0}".format(intStatus))

            strBuffer = pbSend.SerializeToString()
            rosMessage = BinaryData()
            rosMessage.data = strBuffer
            rosMessage.size = len(strBuffer)
            globalPubToSystemMasterStatus.publish(rosMessage)
            self.release_S()

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def notify_cloud(self, refJob):
        rospy.loginfo("enter BusTrajectoryImpInterfaceDataSource::notify_cloud")
        pass

    def write_event(self, refJob):
        rospy.loginfo("enter DfTrajectoryImpInterfaceDataSource::write_event")

    def getTimeval(self):
        return self.mInterVal

    def getModulePrivilege(self):
        try:
            pass
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def block_S(self):
        rospy.logwarn("DfTrajectoryImpInterfaceDataSource::block_S")
        self.s_lock.wait()

    def release_S(self):
        rospy.logwarn("DfTrajectoryImpInterfaceDataSource::release_S")
        rospy.loginfo("self.s_lock.isSet():{0}".format(self.s_lock.isSet()))
        if self.s_lock.isSet() == False:
            self.s_lock.set()

    def subRequestFinish(self, strVersion, intStatus):
        rospy.loginfo(
            "DfTrajectoryImpInterfaceDataSource recv subRequestFinish src : {0}  status: {1}".format(strVersion,
                                                                                                     intStatus))
        self.intFirstStatus = intStatus
        self.release_S()
