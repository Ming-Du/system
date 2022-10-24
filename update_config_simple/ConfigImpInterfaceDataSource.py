#!/usr/bin/env python

import json
import os
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

import traceback

from CommonHttpUtils import CommonHttpUtils
import rospy
from FileUtils import FileUtils

instanceCommonUtils = CommonUtilsCompare()
instanceCacheUtils = CacheUtils("/home/mogo/data/StartupConfigCache.json")
instanceReadConfigFile = CommonUtilsReadFile()
instanceCommonHttpUtils = CommonHttpUtils()


class ConfigImpInterfaceDataSource(InterfaceDataSource):
    strUrlList = None
    strUrlSync = None
    mScheduler = None
    mEnumDataSourceType = None
    mCacheUtils = None
    mStrConfigFileName = None
    mCommonPara = None
    mInterval = None

    def __init__(self):
        try:
            self.strUrlList = "https://mdev.zhidaohulian.com/config/file/list"
            self.strUrlSync = "https://mdev.zhidaohulian.com/config/file/sync"
            self.mEnumDataSourceType = EnumDataSourceType.DATA_SOURCE_UPDATE_CONFIG
            self.mStrConfigFileName = "/home/mogo/data/UpdateConfigCache.json"
            self.mCommonPara = CommonPara()
            self.mCommonPara.initPara()
            self.mInterval = 120
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
        strConfigFilePath = "/home/mogo/data/vehicle_monitor/UpdateConfig.json"
        intError = 0
        try:
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

    def getModuleName(self):
        return "ConfigImpInterfaceDataSource"

    def process_topic(self, strTopicName, msg):
        pass

    def process_cycle(self, dictParameter):
        pass

    def readHttpNewList(self, strRespContent, refJob):
        intError = 0
        dictResult = {}

        intLenData = 0
        dictResult = None
        while True:
            if len(strRespContent) == 0:
                rospy.loginfo("strRespContent:{0}".format(strRespContent))
                intError = -1
                break
            try:
                dictResult = json.loads(strRespContent)
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            if len(dictResult) == 0:
                intError = -1
                break
            if (dictResult.has_key('errcode')) and (dictResult['errcode'] != 0):
                intError = -1
                break
            if dictResult.has_key('data'):
                intLenData = len(dictResult['data'])

            if intLenData == 0:
                intError = -1
                break
            jobItem = None
            for idx in range(0, intLenData):
                jobItem = None
                try:
                    rospy.loginfo("-----  readHttpNewList push idx:{0}".format(idx))
                    strFullFileName = str(dictResult['data'][idx]['filepath'])
                    strMd5 = str(dictResult['data'][idx]['md5'])
                    strUrl = str(dictResult['data'][idx]['content'])
                    intPubTimeStamp = int(dictResult['data'][idx]['commitTime'])
                    intReplyId = dictResult['data'][idx]['id']
                    jobItem = JobItem()
                    jobItem.strFullFileName = strFullFileName
                    rospy.loginfo("push idx:{0},strFullFileName:{1}".format(idx, jobItem.strFullFileName))
                    strFullFileTempName = "{0}.temp".format(jobItem.strFullFileName)
                    jobItem.strFullFileTempName = strFullFileTempName
                    jobItem.strUrl = strUrl
                    jobItem.strMd5 = strMd5
                    jobItem.intReplyId = intReplyId
                    jobItem.intPublishTimeStamp = intPubTimeStamp
                    refJob[0].listJobCollect.append(jobItem)
                except Exception as e:
                    rospy.logwarn('repr(e):{0}'.format(repr(e)))
                    rospy.logwarn('e.message:{0}'.format(e.message))
                    rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            break
            if len(refJob[0].listJobItem) > 0:
                intError = 0
        return intError

    def process_startup(self, dictParameter):
        rospy.logdebug("--------------enter ConfigImpInterfaceDataSource process_startup")
        instanceHttpUtils = CommonHttpUtils()
        dictPostPara = {}
        instanceJob = Job()
        refJob = [instanceJob]
        rospy.logdebug("dict_info:{0}".format(self.mCommonPara.dictCarInfo))
        intHttpCode = 0
        errcode = 0
        try:
            dictPostPara['sn'] = self.mCommonPara.dictCarInfo['car_plate']
            dictPostPara['mac'] = self.mCommonPara.dictCarInfo['mac']
            intHttpCode, strRespContent = instanceHttpUtils.sendSimpleHttpRequestWithHeader(self.strUrlList,
                                                                                            dictPostPara)
            if intHttpCode == 200:
                errcode = self.readHttpNewList(strRespContent, refJob)
                rospy.loginfo("process_startup errcode:{0}".format(errcode))

            if errcode == 0 and len(refJob[0].listJobCollect) > 0:
                # instanceJob.listJobCollect = listJobItem
                rospy.loginfo("---------len(refJob[0].listJobCollec):{0}".format(len(refJob[0].listJobCollect)))

            intError = self.getNeedUpdateFile(refJob)
            refJob[0].handlerDataSource = self
            rospy.logwarn("#######  process_startup ----intError:{0}".format(intError))
            if intError == 0:
                self.pushSimpleJobScheduler(self, refJob)
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
            rospy.loginfo("++++getNeedUpdateFile+++++++: refJob:{0}".format(refJob))
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intError

    def pushJobScheduler(self, refDataSource, refJob):
        try:
            refJob[0].enumJobType = EnumJobType.JOB_TYPE_DELAY
            refJob[0].handlerDataSource = self
            if len(refJob) > 0:
                self.mScheduler.run_block_executor_job(refJob[0])
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def pushSimpleJobScheduler(self, refDataSource, refJob):
        try:
            refJob[0].enumJobType = EnumJobType.JOB_TYPE_DELAY
            refJob[0].handlerDataSource = self
            self.mScheduler.add_task(refDataSource, refJob)
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
        rospy.logdebug("-------------------- enter checkAtomicFeature -----------------------")
        pass

    def install_stage_path(self, refJob):
        pass
        # print "--------------------enter install_stage_path --------------------  "
        # for idx in range(len(refJob.listJobCollect)):
        #     if len(refJob.listJobCollect[idx].strFullFileStageName) > 0:
        #         strStageName = refJob.listJobCollect[idx].strFullFileStageName
        #         strFolderName = os.path.dirname(strStageName)
        #         if os.path.exists(strFolderName):
        #             pass
        #         else:
        #             os.makedirs(strFolderName)
        #             os.chmod(strFolderName, 0777)
        #     print "----------------  refJob.listJobCollect[idx].strFullFileTempName:{0}".format(
        #         refJob.listJobCollect[idx].strFullFileTempName)
        #     print "----------------  refJob.listJobCollect[idx].strFullFileStageName:{0}".format(
        #         refJob.listJobCollect[idx].strFullFileStageName)
        #     shutil.copyfile(refJob.listJobCollect[idx].strFullFileTempName,
        #                     refJob.listJobCollect[idx].strFullFileStageName)

    def install_dst_path(self, refJob):
        rospy.logdebug("---------------enter install_dst_path---------------------- ")
        try:
            for idx in range(len(refJob.listJobCollect)):
                shutil.copyfile(refJob.listJobCollect[idx].strFullFileTempName,
                                refJob.listJobCollect[idx].strFullFileName)
                strCurrentFile = refJob.listJobCollect[idx].strFullFileName
            strSnLinkConfig = ""
            if self.mCommonPara.dictCarInfo.has_key('car_plate') and len(self.mCommonPara.dictCarInfo['car_plate']) > 0:
                strSnLinkConfig = "/home/mogo/data/vehicle_monitor/{0}/slinks.cfg".format(self.mCommonPara.dictCarInfo['car_plate'])
            strCommonLinkConfig = "/home/mogo/data/vehicle_monitor/slinks.cfg"
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
        rospy.logdebug("--------------------------------enter write_cache_file-----------------")
        try:
            for idx in range(len(refJob.listJobCollect)):
                intLocalModifyTimeStamp = int(os.path.getmtime(refJob.listJobCollect[idx].strFullFileName))
                strUrl = refJob.listJobCollect[idx].strUrl
                strMd5 = refJob.listJobCollect[idx].strMd5
                intPublishTimestamp = refJob.listJobCollect[idx].intPublishTimeStamp
                self.mCacheUtils.writeFileCacheInfo(refJob.listJobCollect[idx].strFullFileName, strUrl, strMd5,
                                                    intPublishTimestamp,
                                                    intLocalModifyTimeStamp)
                if os.path.exists(refJob.listJobCollect[idx].strFullFileTempName):
                    os.remove(refJob.listJobCollect[idx].strFullFileTempName)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def notify_pad(self, refJob):
        rospy.logdebug("---------------------------enter notify_pad---------------------------- ")
        pass

    def notify_cloud(self, refJob):
        rospy.logdebug("----------------------------enter notify_cloud------------------------")
        try:
            self.mCommonPara.initPara()
            for idx in range(len(refJob.listJobCollect)):
                dictReceiptContent = {}
                dictReceiptContent['id'] = refJob.listJobCollect[idx].intReplyId
                dictReceiptContent['md5'] = refJob.listJobCollect[idx].strMd5
                dictReceiptContent['version'] = "version"
                dictReceiptContent['filepath'] = refJob.listJobCollect[idx].strFullFileTempName
                dictReceiptContent['pullStatus'] = 1
                dictReceiptContent['sn'] = self.mCommonPara.dictCarInfo['car_plate']
                instanceCommonHttpUtils.sendSimpleHttpRequestWithHeader(self.strUrlSync, dictReceiptContent)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_event(self, refJob):
        rospy.logdebug("------------------enter write_event-------------------------------")

    def getTimeval(self):
        return self.mInterval
