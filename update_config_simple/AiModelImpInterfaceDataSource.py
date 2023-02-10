#!/usr/bin/env python

import json
import os
import traceback

import shutil
from datetime import time

from InterfaceDataSource import InterfaceDataSource
from CommonUtilsCompare import CommonUtilsCompare
from Job import Job
from JobItem import JobItem

from CacheUtils import CacheUtils
from CommonUtilsReadFile import CommonUtilsReadFile
from CommonPara import CommonPara
from CommonHttpUtils import CommonHttpUtils
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool
from EnumDataSourceType import EnumDataSourceType
import rospy
import requests
from FileUtils import FileUtils

from EnumJobType import EnumJobType
from CommonEventUtils import CommonEventUtils

instanceCommonUtils = CommonUtilsCompare()
instanceReadConfigFile = CommonUtilsReadFile()
instanceCacheUtils = CacheUtils("/home/mogo/data/AiModelCache.json")
instanceCommonHttpUtils = CommonHttpUtils()
from FileUtils import FileUtils
import sys
from CommonWgetFileRestore import CommonWgetFileRestore
instanceCommonUtilsCompare = CommonUtilsCompare()
from CommonDataSourceUtil import CommonDataSourceUtil
sys.path.append(os.path.dirname(__file__) + '/../mogo_reporter/script/')
sys.path.append('../mogo_reporter/script/')
from get_msg_by_code import gen_report_msg

def simpleHttpsQuery(strIp, strPort, strApiName, dictQueryCondition):
    strJsonResult = ""
    dictHeader = {}
    dictHeader['Content-Type'] = "application/json"
    try:
        url = "https://{0}{1}".format(strIp, strApiName)
        rospy.logdebug("simpleHttpsQuery url:{0}".format(url))
        ret = requests.post(url, headers=dictHeader, data=json.dumps(dictQueryCondition), timeout=3, verify=False)
        s = ret.content.decode('utf8')
        rospy.logdebug("simpleHttpsQuery s:{0}".format(s))
        j = json.loads(s)
        strJsonResult = json.dumps(j, sort_keys=True, indent=4)
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    return strJsonResult


def link_file(strDownStageLocationFileMap, strStandardLocationFileMap):
    ret = 0
    try:
        if os.path.exists(strDownStageLocationFileMap):
            while True:
                if (os.path.exists(strStandardLocationFileMap)) and (
                        os.readlink(strStandardLocationFileMap) == strDownStageLocationFileMap):
                    rospy.logdebug("############ link file:{0}  and target_file:{1} name normal".format(
                        strStandardLocationFileMap, strDownStageLocationFileMap))
                    break
                if (os.path.exists(strStandardLocationFileMap)) and (
                        os.readlink(strStandardLocationFileMap) != strDownStageLocationFileMap):
                    rospy.logdebug("############ link file:{0}  and target_file:{1} name abnormal".format(
                        strStandardLocationFileMap, strDownStageLocationFileMap))
                    os.remove(strStandardLocationFileMap)
                    os.symlink(strDownStageLocationFileMap, strStandardLocationFileMap)
                    ret = 1
                    break
                if not os.path.exists(strStandardLocationFileMap):
                    rospy.logdebug("link file: {0} not exists ,now create ".format(strStandardLocationFileMap))
                    os.symlink(strDownStageLocationFileMap, strStandardLocationFileMap)
                    ret = 1
                    break
                break
        else:
            rospy.logwarn("src file:{0} not exists, link failed".format(strDownStageLocationFileMap))
            ret = -1

    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    return ret

instanceCommonDataSourceUtil = CommonDataSourceUtil()
class AiModelImpInterfaceDataSource(InterfaceDataSource):
    strUrlList = None
    strUrlSync = None
    mScheduler = None
    mEnumDataSourceType = None
    mCacheUtils = None
    mStrConfigFileName = None
    mCommonPara = None
    mIntTimeval = None
    mFiles = None
    instanceCommonWgetFileRestore = None

    def __init__(self):
        try:
            self.strUrlList = "https://mdev.zhidaohulian.com:443/config/ai/list"
            self.strUrlSync = "https://mdev.zhidaohulian.com:443/config/ai/sync"
            self.mEnumDataSourceType = EnumDataSourceType.DATA_SOURCE_UPDATE_CONFIG
            self.mStrConfigFileName = "/home/mogo/data/AiModelCache.json"
            self.mCommonPara = CommonPara()
            self.mCommonPara.initPara()
            self.mIntTimeval = 432000
            self.mFiles = {}
            self.instanceCommonWgetFileRestore = CommonWgetFileRestore()

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def setScheduler(self, instanceScheduler):
        self.mScheduler = instanceScheduler

    def setCacheUtils(self, instanceCacheUtil):
        self.mCacheUtils = instanceCacheUtil

    def getVersion(self):
        pass

    def configure(self):
        intError = 0
        try:
            strConfigFilePath = "/home/mogo/data/vehicle_monitor/AiModelConfig.json"
            dictConfig = {}
            intError, dictConfig = instanceReadConfigFile.readJsonConfig(strConfigFilePath)
            if intError == 0 and len(dictConfig) > 0:
                if dictConfig.has_key("url_list"):
                    self.strUrlList = dictConfig['url_list']
                if dictConfig.has_key("url_sync"):
                    self.strUrlSync = dictConfig['url_sync']
                if dictConfig.has_key("timeval"):
                    self.mIntTimeval = int(dictConfig['timeval'])
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intError

    def init_module(self):
        self.setCacheUtils(instanceCacheUtils)

    def destroy_module(self):
        pass

    def readHttpList(self, strRespContent, refJob):
        intError = 0
        dictResult = {}
        rospy.loginfo("strRespContent:{0}".format(strRespContent))
        intLenData = 0
        listJobItem = []
        dictResult = None

        intErrorCode = None
        strMsg = None
        intMapId = None
        intPid = None
        strCosPath = None
        strPath = None
        strMd5 = None
        strMapVersion = None
        strUpdateTime = None

        while True:
            try:
                if len(strRespContent) == 0:
                    intError = -1
                    break
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            try:
                dictResult = json.loads(strRespContent)
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            try:
                if len(dictResult) == 0:
                    intError = -1
                    break
                if (dictResult.has_key('errcode')) and (dictResult['errcode'] != 0):
                    intError = -1
                    break
                if dictResult.has_key('data') and dictResult['data'] is not None:
                    intLenData = len(dictResult['data'])

                if intLenData == 0:
                    intError = -1
                    break
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

            dictResult = None
            try:
                dictResult = json.loads(strRespContent)
                if dictResult is not None and len(dictResult) > 0:
                    intErrorCode = str(dictResult['errcode'])
                    strErrorMsg = str(dictResult['msg'])
                    strMapVersion = str(dictResult['data']['mapVersion'])
                    intTimeStamp = int(dictResult['data']['timestamp'])
                    strUpdateTime = str(dictResult['data']['updateTime'])
                    intId = int(dictResult['data']['id'])

                    fileCollect = dictResult['data']['file']
                    for idx in range(len(fileCollect)):
                        strCosPath = fileCollect[idx]['cosPath']
                        rospy.logdebug("************************   readHttpList idx:{0}  strCosPath:{1}".format(idx, strCosPath))
                        strFilePath = fileCollect[idx]['path']
                        rospy.logdebug("***********************  readHttpList idx:{0}  strFilePath:{1}".format(idx, strFilePath))
                        strMd5 = fileCollect[idx]['md5']
                        rospy.logdebug("***********************  readHttpList idx:{0}  strMd5:{1}".format(idx, strMd5))
                        jobItem = JobItem()
                        jobItem.strFullFileName = strFilePath
                        jobItem.strUrl = strCosPath
                        jobItem.strMd5 = strMd5
                        jobItem.intReplyId = intId
                        jobItem.intPublishTimeStamp = intTimeStamp
                        refJob[0].setStrJobFeature(self.getModuleName(),intTimeStamp)
                        strFullFileTempName = self.instanceCommonWgetFileRestore.processSingleFile(refJob[0].strDownTempFolder,jobItem.strUrl)
                        jobItem.strFullFileTempName = strFullFileTempName
                        refJob[0].listJobCollect.append(jobItem)
                        refJob[0].strJobId = "define_job_id"
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            break
            if len(refJob[0].listJobCollect) > 0:
                intError = 0
        return intError

    def process_topic(self, strTopicName, msg):
        pass

    def process_cycle(self, dictParameter):
        try:
            instanceHttpUtils = CommonHttpUtils()
            dictPostPara = {}
            dictPostPara['vehicleConfSn'] = self.mCommonPara.dictCarInfo['car_plate']
            intHttpCode, strRespContent = instanceHttpUtils.sendSimpleHttpRequestWithHeader(self.strUrlList,
                                                                                            dictPostPara)
            if intHttpCode == -1:
                return

            listJobItem = []
            instanceJob = Job()
            refJob = [instanceJob]
            intError = 0
            if intHttpCode == 200:
                intError = self.readHttpList(strRespContent, refJob)
            rospy.loginfo("================ refJob[0].listJobCollect:{0}".format(refJob[0].listJobCollect))
            if intError == 0 and len(refJob[0].listJobCollect) > 0:
                intError = self.getNeedUpdateFile(refJob)
            if intError == 0:
                self.pushJobScheduler(self, refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def process_startup(self, dictParameter):
        try:
            pass
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

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
            refJob[0].enumJobType = EnumJobType.JOB_TYPE_DELAY
            refJob[0].handlerDataSource = self
            rospy.loginfo("=======================    pushJobScheduler,listCollect: {0} ".format(refJob[0].listJobCollect))
            intFileRepeat = 0
            if intFileRepeat == 0 and len(refJob[0].listJobCollectUpdate) > 0:
                rospy.loginfo("##### push AI task")
                self.mScheduler.add_job_to_queue(refDataSource, refJob)
            else:
                rospy.loginfo("##ignore  repleat  AI task")

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def schedulerFinishAction(self, refJob):
        rospy.logdebug(
            "---------------------------enter  AiModelImpInterfaceDataSource schedulerFinishAction--------------- ")
        try:
            self.checkAtomicFeature(refJob)
            self.install_stage_path(refJob)
            self.install_dst_path(refJob)
            self.write_cache_file(refJob)
            self.notify_pad(refJob)
            self.notify_cloud(refJob)
            self.write_event(refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def checkAtomicFeature(self, refJob):
        rospy.loginfo("enter AiModelImpInterfaceDataSource::checkAtomicFeature")
        try:
            instanceCommonDataSourceUtil.checkAtomicFeature(refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


    def install_stage_path(self, refJob):
        rospy.logdebug(
            "---------------------------enter  AiModelImpInterfaceDataSource install_stage_path--------------- ")
        pass


    def install_dst_path(self, refJob):
        rospy.logdebug("-----enter  AiModelImpInterfaceDataSource install_dst_path--")
        try:
            instanceCommonDataSourceUtil.install_dst_path(refJob)
            strSnLinkConfig = ""
            if self.mCommonPara.dictCarInfo.has_key('car_plate') and len(self.mCommonPara.dictCarInfo['car_plate']) > 0:
                strSnLinkConfig = "/home/mogo/data/vehicle_monitor/{0}/slinks_AiModel.cfg".format(
                    self.mCommonPara.dictCarInfo['car_plate'])
            strCommonLinkConfig = "/home/mogo/data/vehicle_monitor/slinks_AiModel.cfg"
            rospy.loginfo("strSnLinkConfig:{0}".format(strSnLinkConfig))
            rospy.loginfo("strCommonLinkConfig:{0}".format(strCommonLinkConfig))
            instanceFileUtils = FileUtils()
            instanceFileUtils.linkFileAccordConfig(strCommonLinkConfig)
            instanceFileUtils.linkFileAccordConfig(strSnLinkConfig)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_cache_file(self, refJob):
        rospy.logdebug("---enter  AiModelImpInterfaceDataSource write_cache_file---")
        try:
            for idx in range(len(refJob.listJobCollectUpdate)):
                if not os.path.exists(refJob.listJobCollectUpdate[idx].strFullFileName):
                    rospy.logwarn("file:{0} not exists:".format(refJob.listJobCollectUpdate[idx].strFullFileName))
                    continue
                intLocalModifyTimeStamp = int(os.path.getmtime(refJob.listJobCollectUpdate[idx].strFullFileName))
                strUrl = refJob.listJobCollectUpdate[idx].strUrl
                strMd5 = refJob.listJobCollectUpdate[idx].strMd5
                intPublishTimestamp = refJob.listJobCollectUpdate[idx].intPublishTimeStamp
                self.mCacheUtils.writeFileCacheInfo(refJob.listJobCollectUpdate[idx].strFullFileName, strUrl, strMd5, intPublishTimestamp,
                                                    intLocalModifyTimeStamp)
                if os.path.exists(refJob.listJobCollectUpdate[idx].strFullFileTempName):
                    os.remove(refJob.listJobCollectUpdate[idx].strFullFileTempName)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def notify_pad(self, refJob):
        try:
            pass
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def notify_cloud(self, refJob):
        rospy.logdebug("-----enter AiModelImpInterfaceDataSource notify_cloud---")
        intCompleteFlag = -1
        try:
            for idx in range(len(refJob.listJobCollectUpdate)):
                if refJob.listJobCollectUpdate[idx].intStatus != 0:
                    intCompleteFlag = 0
                    break
                intCompleteFlag = 1
            if intCompleteFlag == 1:
                dictReceiptContent = {}
                dictReceiptContent['mapId'] = refJob.listJobCollectUpdate[0].intReplyId
                dictReceiptContent['pid'] = refJob.listJobCollectUpdate[0].intReplyId
                dictReceiptContent['vehicleConfSn'] = self.mCommonPara.dictCarInfo['car_plate']
                instanceCommonHttpUtils.sendSimpleHttpRequestWithHeader(self.strUrlSync, dictReceiptContent)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_event(self, refJob):
        try:
            rospy.loginfo("---enter  AiModelImpInterfaceDataSource write_event------")
            instanceCommonEventUtils = CommonEventUtils()
            instanceCommonEventUtils.SaveEventToFile("update_config_simple.yaml", "ISYS_CONFIG_UPDATE_AI_MODEL", "/update_config_simple", "")
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def getTimeval(self):
        rospy.logdebug("-----enter  AiModelImpInterfaceDataSource getTimeval-----")
        return self.mIntTimeval

    def getModuleName(self):
         return "AiModelImpInterfaceDataSource"

    def pushSimpleJobScheduler(self, refDataSource, refJob):
        try:
            refJob[0].enumJobType = EnumJobType.JOB_TYPE_DELAY
            refJob[0].handlerDataSource = self
            self.mScheduler.add_task(refDataSource, refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def relink(self):
        rospy.logdebug("---------------enter relink---------------------- ")
        try:
            strSnLinkConfig = ""
            if self.mCommonPara.dictCarInfo.has_key('car_plate') and len(self.mCommonPara.dictCarInfo['car_plate']) > 0:
                strSnLinkConfig = "/home/mogo/data/vehicle_monitor/{0}/slinks_AiModel.cfg".format(
                    self.mCommonPara.dictCarInfo['car_plate'])
            strCommonLinkConfig = "/home/mogo/data/vehicle_monitor/slinks_AiModel.cfg"
            rospy.loginfo("strSnLinkConfig:{0}".format(strSnLinkConfig))
            rospy.loginfo("strCommonLinkConfig:{0}".format(strCommonLinkConfig))
            instanceFileUtils = FileUtils()
            instanceFileUtils.linkFileAccordConfig(strCommonLinkConfig)
            instanceFileUtils.linkFileAccordConfig(strSnLinkConfig)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def pushBlockJobScheduler(self, refDataSource, refJob):
        try:
            refJob[0].enumJobType = EnumJobType.JOB_TYPE_DELAY
            refJob[0].handlerDataSource = self
            if len(refJob) > 0:
                self.mScheduler.run_block_executor_job(refJob[0])
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
