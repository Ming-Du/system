#!/usr/bin/env python
import logging

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
from CommonWgetFileRestore import CommonWgetFileRestore
instanceCommonUtils = CommonUtilsCompare()
instanceReadConfigFile = CommonUtilsReadFile()
instanceScheduler = CommonSchedulerImpInterfaceTaskSchedulingPool()
instanceCommonUtilsCompare = CommonUtilsCompare()
instanceCacheUtils = CacheUtils("/home/mogo/data/trajectory_agent_cache_record_V260.json")

globalProcessRequestPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ProcessRequestPool')

globalPubToSystemMasterStatus = rospy.Publisher("/trajectory_agent/cmd/status", BinaryData, queue_size=1000)
from EnumTrajResult import EnumTrajResult
from CommonPrivilege import CommonPrivilege
instanceCommonPrivilege = CommonPrivilege()


def getCarDirName():
    strDirFlag = ""
    while True:
        if instanceCommonPrivilege.strCarType == "jinlv" or instanceCommonPrivilege.strCarType == "sweeper" or instanceCommonPrivilege.strCarType == "kaiwo":
            strDirFlag = "JL"
            break
        if instanceCommonPrivilege.strCarType == "df":
            strDirFlag = "DF"
            break
        if instanceCommonPrivilege.strCarType == "hq":
            strDirFlag = "HQ"
            break
        break
    return strDirFlag

def subFloat(floatValue):
    strFullValue = ""
    try:
        strFloat = "{0}".format(floatValue)
        listStr = strFloat.split(".")
        strNewPart2 = ""
        if len(listStr) == 2:
            if len(listStr[1]) > 5:
                strPart2 = listStr[1]
                strNewPart2 = strPart2[0:5]
            if len(listStr[1]) == 5:
                strNewPart2 = listStr[1]
            if len(listStr[1]) < 5 and len(listStr[1]) > 0:
                strNewPart2 = listStr[1]
                while True:
                    strNewPart2 = strNewPart2 + '0'
                    curLen = len(strNewPart2)
                    if curLen == 5:
                        break
            strFullValue = "{0}.{1}".format(listStr[0], strNewPart2)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    return strFullValue


def CheckFileExistsByXAndY(floatStartX, floatStartY, floatEndX, floatEndY):
    ret = EnumTrajResult.ENUMTRAJRESULT_V260_SEARCH_LAT_LON_FAILED
    try:
        strFileName1 = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/{4}/traj_{0}_{1}_{2}_{3}_dpqp.csv".format(
            subFloat(floatStartX), subFloat(floatStartY), subFloat(floatEndX), subFloat(floatEndY), getCarDirName())
        strFileName2 = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/{4}/stop_{0}_{1}_{2}_{3}_dpqp.txt".format(
            subFloat(floatStartX), subFloat(floatStartY), subFloat(floatEndX), subFloat(floatEndY), getCarDirName())
        rospy.logwarn("CheckFileExistsByXAndY strFileName1:{0}".format(strFileName1))
        rospy.logwarn("CheckFileExistsByXAndY strFileName2:{0}".format(strFileName2))
        if os.path.exists(strFileName1) and os.path.exists(strFileName2):
            ret = EnumTrajResult.ENUMTRAJRESULT_V260_SEARCH_LAT_LON_SUCCESS
        else:
            ret = EnumTrajResult.ENUMTRAJRESULT_V260_SEARCH_LAT_LON_FAILED
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    return ret


class TrajV260(InterfaceDataSource):
    strUrlList = None
    strUrlSync = None
    mScheduler = None
    mEnumDataSourceType = None
    mCacheUtils = None
    mStrConfigFileName = None
    mCommonPara = None
    mInterVal = None
    mCallerHandler = None
    instanceCommonWgetFileRestore = None

    def __init__(self):
        rospy.loginfo("enter TrajV260::__init__")
        try:
            self.mEnumDataSourceType = EnumDataSourceType.DATA_SOURCE_UPDATE_CONFIG
            self.mStrConfigFileName = "/home/mogo/data/TrajectoryConfigCache_V260.json"
            self.mCommonPara = CommonPara()
            self.mCommonPara.initPara()
            self.mInterVal = 120
            self.instanceCommonWgetFileRestore = CommonWgetFileRestore()
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def setScheduler(self, instanceScheduler):
        rospy.loginfo("enter TrajV260::setScheduler")
        try:
            self.mScheduler = instanceScheduler
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def setCacheUtils(self, instanceCacheUtil):
        rospy.loginfo("enter TrajV260::setCacheUtils")
        try:
            self.mCacheUtils = instanceCacheUtil
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def getModuleName(self):
        return "df_trajectory_260"

    def getVersion(self):
        pass

    def configure(self):
        rospy.loginfo("enter TrajV260::configure")
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
        rospy.loginfo("enter TrajV260::init_module")
        self.setCacheUtils(instanceCacheUtils)

    def destroy_module(self):
        pass

    def topicMsgCallbackStartup(self, msg, lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, floatStartX,
                                floatStartY, floatEndX, floatEndY):
        try:
            rospy.loginfo("enter TrajV260::topicMsgCallbackStartup")
            rospy.loginfo(
                "TrajV260::topicMsgCallbackStartup lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3}, strStopMd5:{4}, floatStartX:{5}, floatStartY:{6}, floatEndX:{7}, floatEndY:{8})".format(
                    lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, floatStartX, floatStartY, floatEndX,
                    floatEndY)
            )
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def call_para(self,lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, floatStartX,
                  floatStartY, floatEndX, floatEndY):
        try:
            intProcessRet = EnumTrajResult.ENUMTRAJRESULT_V260_SEARCH_LAT_LON_FAILED
            rospy.loginfo("enter TrajV260::call_para")
            rospy.loginfo(
                "--------------v260------------processFile: lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3}, strStopMd5:{4}, timestamp:{5},floatStartX:{6}, floatStartY:{7}, floatEndX{8}, floatEndY:{9}".format(
                    lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, floatStartX, floatStartY,
                    floatEndX,
                    floatEndY))
            while True:
                if int(lLineId) > 0:
                    strStandardLocationFileStop = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/{1}/stop_{0}.txt".format(
                        lLineId,getCarDirName())
                    strStandardLocationFileTraj = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/{1}/traj_{0}.csv".format(
                        lLineId,getCarDirName())
                    rospy.logwarn("call_para strStandardLocationFileStop:{0}".format(strStandardLocationFileStop))
                    rospy.logwarn("call_para strStandardLocationFileTraj:{0}".format(strStandardLocationFileTraj))

                if int(timestamp) > 0 or len(strTrajUrl.strip()) == 0 or len(strTrajMd5.strip()) == 0 or len(
                        strStopUrl.strip()) == 0 or len(strStopMd5.strip()) == 0 and float(floatStartX) > float(0.0) and float(floatStartY) > float(0.0) and float(floatEndX) > float(
                        0.0) and float(floatEndY) > float(0.0):
                    if os.path.exists(strStandardLocationFileTraj) and os.path.exists(strStandardLocationFileStop):
                        intProcessRet = EnumTrajResult.ENUMTRAJRESULT_V260_TRAJ_WARNING
                        rospy.loginfo("local line search result:{0}".format(intProcessRet))
                    else:
                        intProcessRet = CheckFileExistsByXAndY(floatStartX, floatStartY, floatEndX, floatEndY)
                        rospy.loginfo("local xy search result:{0}".format(intProcessRet))
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intProcessRet

    def transaction(self,lLineId,strTrajUrl, strTrajMd5, strStopUrl, strStopMd5,timestamp,floatStartX,floatStartY,floatEndX,floatEndY):
        try:
            rospy.loginfo("enter TrajV260::transaction")
            rospy.loginfo(
                "call_process: recv  lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3},strStopMd5:{4},timestamp:{5},strVersion:{6}".format(
                    lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, floatStartX, floatStartY,
                    floatEndX, floatEndY))
            downJob = Job()
            listDownJob = []
            # call process File
            while True:
                if lLineId == 0 or lLineId < 0:
                    break
                if len(strTrajUrl) == 0:
                    break
                if len(strTrajMd5) == 0:
                    break
                if len(strStopUrl) == 0:
                    break
                if len(strStopMd5) == 0:
                    break
                if int(timestamp) < 0 or int(timestamp) == 0:
                    break
                strStandardLocationFileStop = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/{1}/stop_{0}.txt".format(
                    lLineId,getCarDirName())
                strStandardLocationFileTraj = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/{1}/traj_{0}.csv".format(
                    lLineId,getCarDirName())
                jobItemStop = JobItem()
                jobItemStop.strFullFileName = strStandardLocationFileStop
                jobItemStop.strUrl = strStopUrl
                jobItemStop.strMd5 = strStopMd5
                jobItemStop.intPublishTimeStamp = timestamp
                downJob.setStrJobFeature(self.getModuleName(), timestamp)
                strFullFileTempName = self.instanceCommonWgetFileRestore.processSingleFile(downJob.strDownTempFolder,
                                                                                           jobItemStop.strUrl)
                jobItemStop.strFullFileTempName = strFullFileTempName

                jobItemTraj = JobItem()
                jobItemTraj.strFullFileName = strStandardLocationFileTraj
                jobItemTraj.strUrl = strTrajUrl
                jobItemTraj.strMd5 = strTrajMd5
                jobItemTraj.intPublishTimeStamp = timestamp
                downJob.setStrJobFeature(self.getModuleName(), timestamp)
                strFullFileTempName = self.instanceCommonWgetFileRestore.processSingleFile(downJob.strDownTempFolder,
                                                                                           jobItemTraj.strUrl)
                jobItemTraj.strFullFileTempName = strFullFileTempName


                downJob.listJobCollect.append(jobItemStop)
                downJob.listJobCollect.append(jobItemTraj)
                downJob.handlerDataSource = self
                listDownJob.append(downJob)
                intError = self.getNeedUpdateFile(listDownJob)
                if intError == 0 and len(listDownJob[0].listJobCollectUpdate) > 0:
                    self.pushJobScheduler(self, listDownJob)
                if intError == 0 and len(listDownJob[0].listJobCollectUpdate) == 0:
                    self.schedulerFinishAction(downJob)
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def process_cycle(self, dictParameter):
        pass

    def process_startup(self, dictParameter):
        pass

    def getNeedUpdateFile(self, refJob):
        rospy.loginfo("enter TrajV260::getNeedUpdateFile")
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
            rospy.loginfo("enter TrajV260::pushJobScheduler")
            refJob[0].enumJobType = EnumJobType.JOB_TYPE_IMMEDIATELY
            refJob[0].handlerDataSource = self
            self.mScheduler.add_job_to_queue(refDataSource, refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def schedulerFinishAction(self, refJob):
        try:
            rospy.loginfo("enter TrajV260::schedulerFinishAction")
            self.checkAtomicFeature(refJob)
            self.install_stage_path(refJob)
            intResult = self.notify_pad(refJob)
            rospy.loginfo("TrajV260::schedulerFinishAction intResult: {0}".format(intResult))
            if intResult == EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_SUCCESS:
                self.install_dst_path(refJob)
                self.write_cache_file(refJob)
                rospy.loginfo("TrajV260::schedulerFinishAction  intResult == 0, access write cache file")
            else:
                rospy.logwarn("TrajV260::schedulerFinishAction intResult != 0, deny  write cache file")

            self.notify_cloud(refJob)
            self.write_event(refJob)
            self.mCallerHandler.subRequestFinish("V260", intResult)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def checkAtomicFeature(self, refJob):
        rospy.loginfo("enter TrajV260::checkAtomicFeature")
        ret = 0
        try:
            for idx in range(len(refJob.listJobCollectUpdate)):
                rospy.logwarn("process file:{0}".format(refJob.listJobCollectUpdate[idx].strFullFileTempName))
                if not os.path.exists(refJob.listJobCollectUpdate[idx].strFullFileTempName):
                    rospy.logwarn("TrajV260::checkAtomicFeature tempFileNotExists:{0}".format(
                        refJob.listJobCollectUpdate[idx].strFullFileTempName))
                    continue
                strStandardMd5 = refJob.listJobCollectUpdate[idx].strMd5
                strInputBase64FileName = refJob.listJobCollectUpdate[idx].strFullFileTempName
                strOriginFileName = "{0}.orig".format(refJob.listJobCollectUpdate[idx].strFullFileTempName)
                refJob.listJobCollectUpdate[idx].strFullFileStageName = strOriginFileName
                if os.path.exists(strOriginFileName):
                    os.remove(strOriginFileName)
                ret, strOutputFilePath = instanceCommonUtilsCompare.fromBase64Restore(strInputBase64FileName,
                                                                                      strOriginFileName)
                if ret == 0:
                    strRealMd5 = instanceCommonUtilsCompare.checkFileMd5(strOutputFilePath)
                    rospy.logwarn("TrajV260::checkAtomicFeature strStandardMd5:{0},realfile:{1}_strRealMd5:{2}".format(
                        strStandardMd5, strOriginFileName, strRealMd5))
                    if strRealMd5 == strStandardMd5:
                        refJob.listJobCollectUpdate[idx].intStatus = 0
                        rospy.logwarn(
                            "TrajV260::checkAtomicFeature strFileName:{0} matched md5".format(strOutputFilePath))
                    if strRealMd5 != strStandardMd5:
                        refJob.listJobCollectUpdate[idx].intStatus = -1
                        rospy.logwarn(
                            "TrajV260::checkAtomicFeature strFileName:{0} not  matched md5".format(strOutputFilePath))
                else:
                    rospy.logwarn(
                        "TrajV260::checkAtomicFeature instanceCommonUtilsCompare.fromBase64Restore:{0}".format(ret))
                    refJob.listJobCollectUpdate[idx].intStatus = -1

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def install_stage_path(self, refJob):
        rospy.loginfo("enter TrajV260::install_stage_path")

    def install_dst_path(self, refJob):
        try:
            rospy.loginfo("enter TrajV260::install_dst_path")
            for idx in range(len(refJob.listJobCollect)):
                if not os.path.exists(refJob.listJobCollect[idx].strFullFileStageName):
                    continue
                shutil.copyfile(refJob.listJobCollect[idx].strFullFileStageName,
                                refJob.listJobCollect[idx].strFullFileName)
                os.remove(refJob.listJobCollect[idx].strFullFileTempName)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_cache_file(self, refJob):
        rospy.loginfo("enter TrajV260::write_cache_file")
        try:
            for idx in range(len(refJob.listJobCollect)):
                if not os.path.exists(refJob.listJobCollect[idx].strFullFileName):
                    continue
                intLocalModifyTimeStamp = int(os.path.getmtime(refJob.listJobCollect[idx].strFullFileName))
                strUrl = refJob.listJobCollect[idx].strUrl
                strMd5 = refJob.listJobCollect[idx].strMd5
                intPublishTimestamp = refJob.listJobCollect[idx].intPublishTimeStamp
                self.mCacheUtils.writeFileCacheInfo(refJob.listJobCollect[idx].strFullFileName, strUrl, strMd5,
                                                    intPublishTimestamp,
                                                    intLocalModifyTimeStamp)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def check_local_files(self, refJob):
        rospy.loginfo("enter TrajV260::check_local_files")
        intResultProcess = EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_FAILED
        try:
            while True:
                if refJob is None:
                    rospy.logwarn("error branch refJob is None")
                    break

                if len(refJob.listJobCollect) < 2:
                    rospy.logwarn("error branch len(refJob.listJobCollect) < 2")
                    intResultProcess = EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_FAILED
                    break
                if len(refJob.listJobCollect) > 2:
                    rospy.logwarn("error branch len(refJob.listJobCollect) > 2")
                    intResultProcess = EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_FAILED
                    break
                if os.path.exists(refJob.listJobCollect[0].strFullFileName) and os.path.exists(
                        refJob.listJobCollect[1].strFullFileName):
                    intResultProcess = EnumTrajResult.ENUMTRAJRESULT_V260_TRAJ_WARNING
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intResultProcess

    def notify_pad(self, refJob):
        rospy.loginfo("enter TrajV260::notify_pad")
        try:
            intResultProcess = EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_FAILED
            intSuccessNum = 0
            for idx in range(len(refJob.listJobCollectUpdate)):
                intTempStatus = -1
                intTempStatus = refJob.listJobCollectUpdate[idx].intStatus
                if intTempStatus == 0:
                    intSuccessNum = intSuccessNum + 1

            while True:
                # 2/2 files success , traj and stop  both download success
                if intSuccessNum == 2 and len(refJob.listJobCollectUpdate) == 2:
                    intResultProcess = EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_SUCCESS
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
                    intResultProcess = EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_SUCCESS
                    break

                # 0/1 files success
                if intSuccessNum == 0 and len(refJob.listJobCollectUpdate) == 1:
                    intResultProcess = self.check_local_files(refJob)
                    break

                if intSuccessNum == 0 and len(refJob.listJobCollectUpdate) == 0 and len(refJob.listJobCollect) == 2:
                    intResultProcess = EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_SUCCESS
                    break

                # local files check
                if intSuccessNum == 0 and len(refJob.listJobCollectUpdate) == 0:
                    intResultProcess = self.check_local_files(refJob)
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intResultProcess

    def notify_cloud(self, refJob):
        rospy.loginfo("enter TrajV260::notify_cloud")

    def write_event(self, refJob):
        rospy.loginfo("enter TrajV260::write_event")

    def getTimeval(self):
        return self.mInterVal

    def getModulePrivilege(self):
        try:
            pass
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def setCallerHandler(self, handler):
        rospy.loginfo("enter TrajV260::setCallerHandler")
        self.mCallerHandler = handler
