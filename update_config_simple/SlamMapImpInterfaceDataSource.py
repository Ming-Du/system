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
from EnumJobType import EnumJobType

instanceCommonUtils = CommonUtilsCompare()
instanceCacheUtils = CacheUtils("/home/mogo/data/SlamMapCache.json")
instanceReadConfigFile = CommonUtilsReadFile()
instanceCommonHttpUtils = CommonHttpUtils()
import sys

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


class SlamMapImpInterfaceDataSource(InterfaceDataSource):
    strUrlList = None
    strUrlSync = None
    mScheduler = None
    mEnumDataSourceType = None
    mCacheUtils = None
    mStrConfigFileName = None
    mCommonPara = None
    mIntTimeval = None
    mFiles = None

    def __init__(self):
        try:
            self.strUrlList = "https://mdev.zhidaohulian.com:443/config/slam/list"
            self.strUrlSync = "https://mdev.zhidaohulian.com:443/config/slam/sync"
            self.mEnumDataSourceType = EnumDataSourceType.DATA_SOURCE_UPDATE_CONFIG
            self.mStrConfigFileName = "/home/mogo/data/SlamMapCache.json"
            self.mCommonPara = CommonPara()
            self.mCommonPara.initPara()
            self.mIntTimeval = 432000
            self.mFiles = {}
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
            strConfigFilePath = "/home/mogo/data/vehicle_monitor/SlamMapConfig.json"
            intError = 0
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

    def createFolder(self, strFolderPath):
        try:
            if not os.path.exists(strFolderPath):
                os.makedirs(strFolderPath)
                os.chmod(strFolderPath, 0777)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def init_module(self):
        self.setCacheUtils(instanceCacheUtils)
        strMapPath = "/home/mogo/data/vehicle_monitor/LidarSLAM_data/map/"
        self.createFolder(strMapPath)
        strkeyFramePath = "/home/mogo/data/vehicle_monitor/LidarSLAM_data/key_frames"
        self.createFolder(strkeyFramePath)
        strTrajPath = "/home/mogo/data/vehicle_monitor/LidarSLAM_data/trajectory"
        self.createFolder(strTrajPath)

    def destroy_module(self):
        pass

    def readHttpList(self, strRespContent, refJob):
        intError = -1
        dictResult = {}
        rospy.logdebug("strRespContent:{0}".format(strRespContent))
        intLenData = 0
        listJobItem = []
        dictResult = None

        intErrorCode = None
        strMsg = None
        intMapId = None
        intPid = None
        strCosPath = None
        # strPath = str(dictResult['data']['path'])
        strPath = None
        strMd5 = None
        strMapVersion = None
        strUpdateTime = None

        while True:
            if len(strRespContent) == 0:
                intError = -1
                break
            try:
                dictResult = json.loads(strRespContent)
            except Exception as e:
                print(str(e))
                print('traceback.format_exc():{0}'.format((traceback.format_exc())))
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
                        strFilePath = fileCollect[idx]['path']
                        strMd5 = fileCollect[idx]['md5']
                        jobItem = JobItem()
                        jobItem.strFullFileName = strFilePath
                        strFullFileTempName = "{0}.temp".format(strFilePath)
                        jobItem.strFullFileTempName = strFullFileTempName
                        jobItem.strUrl = strCosPath
                        jobItem.strMd5 = strMd5
                        jobItem.intReplyId = intId
                        jobItem.intPublishTimeStamp = intTimeStamp
                        jobItem.strVersionMap = strMapVersion
                        refJob[0].listJobCollect.append(jobItem)
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
            if dictParameter["longitude"] == -0.01 or dictParameter["latitude"] == -0.01:
                rospy.loginfo(" slam cannot recv  lat and on ")
            else:
                instanceHttpUtils = CommonHttpUtils()
                dictPostPara = {}
                dictPostPara['vehicleConfSn'] = self.mCommonPara.dictCarInfo['car_plate']
                dictPostPara['lng'] = dictParameter["longitude"]
                dictPostPara['lat'] = dictParameter["latitude"]
                intHttpCode, strRespContent = instanceHttpUtils.sendSimpleHttpRequestWithHeader(self.strUrlList,
                                                                                                dictPostPara)
                instanceJob = Job()
                refJob = [instanceJob]
                intError = 0
                if intHttpCode == 200:
                    listJobItem = self.readHttpList(strRespContent, refJob)
                if len(refJob[0].listJobCollect) > 0:
                    intError = self.getNeedUpdateFile(refJob)
                if intError == 0 and len(refJob[0].listJobCollect) > 0:
                    print "process_cycle === ref[0].listJobCollect:{0}".format(refJob[0].listJobCollect)
                    self.pushJobScheduler(self, refJob)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def process_startup(self, dictParameter):
        pass
        # try:
        #     self.process_cycle(dictParameter)
        # except Exception as e:
        #     rospy.logwarn('repr(e):{0}'.format(repr(e)))
        #     rospy.logwarn('e.message:{0}'.format(e.message))
        #     rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

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
            intFileRepeat = 0
            for idx in range(len(refJob[0].listJobCollectUpdate)):
                strKey = "{0}".format(refJob[0].listJobCollectUpdate[idx].strFullFileTempName)
                rospy.loginfo("=========================== strkey:{0}".format(strKey))
                if self.mFiles.has_key(strKey):
                    rospy.loginfo("!!!!! repeat task happend ,now ignore")
                    intFileRepeat = 1
                    break
                else:
                    self.mFiles[strKey] = 0
            print "==================  self.mFiles:{0}".format(self.mFiles)
            rospy.loginfo("...........................intFileRepeat:{0}".format(intFileRepeat))
            if intFileRepeat == 0:
                rospy.loginfo("##### push slam task")
                self.mScheduler.add_job_to_queue(refDataSource, refJob)
            else:
                rospy.loginfo("##ignore  repleat  slam task")
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
        rospy.logdebug("----------enter slam checkAtomicFeature------------")

    def install_stage_path(self, refJob):
        rospy.logdebug("----------enter slam install_stage_path-------------------------------")
        # for idx in range(len(refJob.listJobCollect)):
        #     shutil.copyfile(refJob.listJobCollect[idx].strFullFileTempName,
        #                     refJob.listJobCollect[idx].strFullFileStageName)
        pass

    def install_dst_path(self, refJob):

        rospy.logdebug("----------enter slam install_dst_path-------------------------------")
        try:
            for idx in range(len(refJob.listJobCollect)):
                link_file(refJob.listJobCollect[idx].strFullFileTempName, refJob.listJobCollect[idx].strFullFileName)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_cache_file(self, refJob):
        rospy.logdebug("----enter slam write_cache_file----")
        try:
            for idx in range(len(refJob.listJobCollect)):
                intLocalModifyTimeStamp = int(os.path.getmtime(refJob.listJobCollect[idx].strFullFileTempName))
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

    def notify_pad(self, refJob):
        rospy.logdebug("----------enter slam notify_pad-----")
        if len(refJob.listJobCollectUpdate) > 0:
            for idx in (range(len(refJob.listJobCollectUpdate))):
                strKey = "{0}".format(refJob.listJobCollectUpdate[idx].strFullFileTempName)
                rospy.loginfo("strkey:{0}".format(strKey))
                if self.mFiles.has_key(strKey):
                    del self.mFiles[strKey]
                    rospy.loginfo("notify_pad......,clear files key:{0}".format(strKey))

    def notify_cloud(self, refJob):
        rospy.logdebug("----enter slam notify_cloud-----")
        try:
            for idx in range(len(refJob.listJobCollect)):
                dictReceiptContent = {}
                dictReceiptContent['version'] = refJob.listJobCollect[idx].strVersionMap
                dictReceiptContent['id'] = refJob.listJobCollect[idx].intReplyId
                dictReceiptContent['vehicleConfSn'] = self.mCommonPara.dictCarInfo['car_plate']
                instanceCommonHttpUtils.sendSimpleHttpRequestWithHeader(self.strUrlSync, dictReceiptContent)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def write_event(self, refJob):
        rospy.logdebug("----enter slam write_event-----")
        self.SaveEventToFile(msg='', code='ISYS_CONFIG_UPDATE_SLAM_MAP', results=list(), actions=list(), level='info')

    def getTimeval(self):
        return self.mIntTimeval

    def getModuleName(self):
        return "SlamMapImpInterfaceDataSource"

    def SaveEventToFile(self, msg='', code='', results=list(), actions=list(), level=''):
        rospy.logdebug("enter SaveEventToFile")
        json_msg = {}
        if 1:
            try:
                json_msg = gen_report_msg("update_config_simple.yaml", code, "/update_config_simple")
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        rospy.logdebug("event json_msg:{0}".format(json_msg))
        if json_msg == {}:  # if not used pb or call function error, used local config
            cur_time = int(time.time())
            msg_dict = {
                "timestamp": {
                    "sec": cur_time,
                    "nsec": int((time.time() - cur_time) * 1000000000)},
                "src": "/hd_map_agent",
                "code": code,
                "level": level,
                "result": results,
                "action": actions,
                "msg": msg
            }
            json_msg = json.dumps(msg_dict)
        try:
            with open("/home/mogo/data/log/msg_log/system_master_report.json", 'a+') as fp:
                fp.write(json_msg + '\n')
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
