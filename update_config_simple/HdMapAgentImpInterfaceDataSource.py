#!/usr/bin/env python
import json
import os
import sys
import time
import traceback
from os import path

import requests
import rospy

import shutil

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

from EnumJobType import EnumJobType

from CacheUtils import CacheUtils
from CommonEventUtils import CommonEventUtils
from CommonWgetFileRestore import CommonWgetFileRestore

sys.path.append(os.path.dirname(__file__) + '/../mogo_reporter/script/')
sys.path.append('../mogo_reporter/script/')
from get_msg_by_code import gen_report_msg

instanceCommonUtils = CommonUtilsCompare()
instanceReadConfigFile = CommonUtilsReadFile()
instanceCommonHttpUtils = CommonHttpUtils()
from CommonDataSourceUtil import CommonDataSourceUtil
instanceCacheUtils = CacheUtils("/home/mogo/data/HdMapCache.json")


def link_file(strDownStageLocationFileMap, strStandardLocationFileMap):
    if strDownStageLocationFileMap is not None:
        rospy.loginfo("strDownStageLocationFileMap:{0}".format(strDownStageLocationFileMap))
    if strStandardLocationFileMap is not None:
        rospy.loginfo("strStandardLocationFileMap:{0}".format(strStandardLocationFileMap))
    ret = 0
    try:
        if os.path.exists(strDownStageLocationFileMap):
            while True:
                if (os.path.exists(strStandardLocationFileMap)) and (
                        os.readlink(strStandardLocationFileMap) == strDownStageLocationFileMap):
                    rospy.loginfo("############ link file:{0}  and target_file:{1} name normal".format(
                        strStandardLocationFileMap, strDownStageLocationFileMap))
                    break
                if (os.path.exists(strStandardLocationFileMap)) and (
                        os.readlink(strStandardLocationFileMap) != strDownStageLocationFileMap):
                    rospy.loginfo("############ link file:{0}  and target_file:{1} name abnormal".format(
                        strStandardLocationFileMap, strDownStageLocationFileMap))
                    os.remove(strStandardLocationFileMap)
                    os.symlink(strDownStageLocationFileMap, strStandardLocationFileMap)
                    ret = 1
                    break
                if not os.path.exists(strStandardLocationFileMap):
                    rospy.loginfo("link file: {0} not exists ,now create ".format(strStandardLocationFileMap))
                    os.symlink(strDownStageLocationFileMap, strStandardLocationFileMap)
                    ret = 1
                    break
                break
        else:
            rospy.loginfo("src file:{0} not exists, link failed".format(strDownStageLocationFileMap))
            ret = -1

    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    return ret

instanceCommonDataSourceUtil = CommonDataSourceUtil()
class HdMapAgentImpInterfaceDataSource(InterfaceDataSource):
    strUrlList = None
    strUrlSync = None
    mScheduler = None
    mEnumDataSourceType = None
    mCacheUtils = None
    mStrConfigFileName = None
    mCommonPara = None
    mIntTimeval = None
    mIntMapId = None
    mIntPid = None
    mFiles = None
    instanceCommonWgetFileRestore = None

    def __init__(self):
        try:
            self.strUrlList = "https://mdev.zhidaohulian.com:443/config/map/list"
            self.strUrlSync = "https://mdev.zhidaohulian.com:443/config/map/sync"
            self.mEnumDataSourceType = EnumDataSourceType.DATA_SOURCE_UPDATE_CONFIG
            self.mStrConfigFileName = "/home/mogo/data/HdMapAgentCache.json"
            self.mCommonPara = CommonPara()
            self.mCommonPara.initPara()
            self.mIntTimeval = 432000
            self.mIntMapId = -1
            self.mIntPid = -1
            self.mFiles = {}
            self.instanceCommonWgetFileRestore = CommonWgetFileRestore()
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def setScheduler(self, instanceScheduler):
        self.mScheduler = instanceScheduler

    def setCacheUtils(self, instanceCacheUtils):
        self.mCacheUtils = instanceCacheUtils

    def getModuleName(self):
        return "HdMapAgentImpInterfaceDataSource"

    def getVersion(self):
        pass

    def configure(self):
        strConfigFilePath = "/home/mogo/data/vehicle_monitor/HdMapAgentConfig.json"
        intError = 0
        dictConfig = {}
        try:
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
        intError = -1

        rospy.loginfo("strRespContent:{0}".format(strRespContent))
        intLenData = 0
        dictResult = {}

        intErrorCode = None
        strMsg = None
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
                rospy.logwarn(str(e))
                rospy.logwarn('traceback.format_exc():{0}'.format((traceback.format_exc())))
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
                    intErrorCode = int(dictResult['errcode'])
                    strMsg = str(dictResult['msg'])
                    self.mIntMapId = str(dictResult['data']['mapId'])
                    self.mIntPid = str(dictResult['data']['pid'])
                    strCosPath = str(dictResult['data']['cosPath'])
                    strBackupLinkPath = "/home/mogo/autopilot/share/hadmap_engine/data/hadmap_data/db.sqlite.backup"
                    strMd5 = str(dictResult['data']['md5'])
                    strMapVersion = str(dictResult['data']['mapVersion'])
                    strUpdateTime = str(dictResult['data']['updateTime'])

                    strTime = "2022-06-30T06:14:52.000+00:00"
                    listSubTime = strUpdateTime.split('+')

                    rospy.loginfo("listSubTime:{0}".format(listSubTime))
                    strSimpleTime = ""
                    if len(listSubTime) == 2:
                        if len(listSubTime[0]) > 0:
                            listSubSubTime = listSubTime[0].split('.000')
                            if len(listSubSubTime) == 2 and len(listSubSubTime[0]) > 0:
                                strSimpleTime = listSubSubTime[0]
                    rospy.loginfo("-------------- strSimpleTime:{0}".format(strSimpleTime))
                    timeArray = time.strptime(strSimpleTime, "%Y-%m-%dT%H:%M:%S")
                    intTranslateUpdateTime = int(time.mktime(timeArray))
                    rospy.loginfo(
                        "call_process: recv  lMapId:{0}, strMapUrl:{1}, strMapMd5:{2},timestamp:{3},strVersion:{4}".format(
                            self.mIntPid, strCosPath, strMd5, intTranslateUpdateTime, strMapVersion))
                    # download map
                    jobItem = JobItem()
                    jobItem.strFullFileStageName = "/home/mogo/data/down_map_agent_stage/map_{0}_{1}".format(
                        self.mIntPid,
                        intTranslateUpdateTime)
                    jobItem.strFullFileName = jobItem.strFullFileStageName
                    jobItem.strUrl = strCosPath
                    jobItem.strMd5 = strMd5
                    jobItem.intReplyId = self.mIntPid
                    jobItem.intPublishTimeStamp = intTranslateUpdateTime
                    refJob[0].setStrJobFeature(self.getModuleName(), jobItem.intPublishTimeStamp)
                    strFullFileTempName = self.instanceCommonWgetFileRestore.processSingleFile(
                        refJob[0].strDownTempFolder, jobItem.strUrl)
                    jobItem.strFullFileTempName = strFullFileTempName
                    jobItem.strLinkPath = strBackupLinkPath
                    refJob[0].listJobCollect.append(jobItem)
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            break
            if len(listJobItem) > 0:
                intError = 0
        return intError

    def process_topic(self, strTopicName, msg):
        pass

    def process_cycle(self, dictParameter):
        try:
            if dictParameter["longitude"] == -0.01 or dictParameter["latitude"] == -0.01:
                rospy.loginfo("cannot recv  lat and on ")
            else:
                instanceHttpUtils = CommonHttpUtils()
                dictPostPara = {'vehicleConfSn': self.mCommonPara.dictCarInfo['car_plate'],
                                'lng': dictParameter["longitude"],
                                'lat': dictParameter["latitude"]}
                intHttpCode, strRespContent = instanceHttpUtils.sendSimpleHttpRequestWithHeader(self.strUrlList,
                                                                                                dictPostPara)
                if intHttpCode == -1:
                    return
                instanceJob = Job()
                refJob = [instanceJob]
                intError = 0
                if intHttpCode == 200:
                    intError = self.readHttpList(strRespContent, refJob)
                if len(refJob[0].listJobCollect) > 0:
                    intError = self.getNeedUpdateFile(refJob)
                if intError == 0:
                    self.pushJobScheduler(self, refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

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
            refJob[0].enumJobType = EnumJobType.JOB_TYPE_DELAY
            refJob[0].handlerDataSource = self
            if len(refJob[0].listJobCollectUpdate) > 0:
                self.mScheduler.add_job_to_queue(refDataSource, refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def schedulerFinishAction(self, refJob):
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
        instanceCommonDataSourceUtil.checkAtomicFeature(refJob)
        pass

    def install_stage_path(self, refJob):
        try:
            instanceCommonDataSourceUtil.install_dst_path(refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def install_dst_path(self, refJob):
        try:
            for idx in range(len(refJob.listJobCollectUpdate)):
                link_file(refJob.listJobCollectUpdate[idx].strFullFileStageName, refJob.listJobCollect[idx].strLinkPath)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_cache_file(self, refJob):
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
        rospy.logdebug(" ===== notify_cloud====  typeof(refJob):{0}".format(refJob))
        try:
            for idx in range(len(refJob.listJobCollectUpdate)):
                if refJob.listJobCollectUpdate[idx].intStatus != 0:
                    continue
                dictReceiptContent = {'mapId': refJob.handlerDataSource.mIntMapId,
                                  'pid': refJob.handlerDataSource.mIntPid,
                                  'vehicleConfSn': self.mCommonPara.dictCarInfo['car_plate']}
                instanceCommonHttpUtils.sendSimpleHttpRequestWithHeader(self.strUrlSync, dictReceiptContent)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_event(self, refJob):
        try:
            instanceCommonEventUtils = CommonEventUtils()
            instanceCommonEventUtils.SaveEventToFile("hd_map.yaml", "ISYS_CONFIG_UPDATE_HADMAP", "/update_config_simple", "")
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def getTimeval(self):
        return self.mIntTimeval

    def relink(self):
        pass

