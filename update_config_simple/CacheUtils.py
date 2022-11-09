#!/usr/bin/env python

import rospy
import json
import os
import traceback
import sys

sys.path.append(".")
from EnumVersion import EnumVersion


class CacheUtils:
    dictFileStorage = None
    strDictSaveTime = None

    def __init__(self, strCacheFilePath):
        self.dictFileStorage = {}
        self.strDictSaveTime = strCacheFilePath
        strFolderName = os.path.dirname(self.strDictSaveTime)
        if not os.path.exists(strFolderName):
            os.makedirs(strFolderName)
            os.chmod(strFolderName, 0777)
        self.restoreIndex()

    def getId(self, strFileName):
        strId = "{0}".format(strFileName)
        return strId

    def writeFileCacheInfo(self, strFileName, strUrl, strMd5, intPublishTimestamp, intModifyTimestamp):
        rospy.logdebug(
            "process WriteFileCacheInfo: strFileName:{0}, strUrl:{1}, strMd5:{2},intPublishTimestamp:{3},"
            "intModifyTimestamp:{4}".format(
                strFileName, strUrl, strMd5, intPublishTimestamp, intModifyTimestamp))
        try:
            dictFileInfo = {}
            strId = self.getId(strFileName)
            dictFileInfo['id'] = strId
            dictFileInfo['url'] = strUrl
            dictFileInfo['publish_timestamp'] = intPublishTimestamp
            dictFileInfo['md5'] = strMd5
            dictFileInfo['modify_timestamp'] = intModifyTimestamp
            self.dictFileStorage[strId] = dictFileInfo
            json.dump(self.dictFileStorage, open(self.strDictSaveTime, 'w'))


        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def CheckIdExists(self, strFileName, strMd5):
        bExists = True
        try:
            strId = self.getId(strFileName, strMd5)
            if self.dictFileStorage.has_key(strId):
                bExists = True
            else:
                bExists = False
            rospy.loginfo("CheckTrajFileCacheExists check file:{0}, result:{1}".format(strFileName, bExists))
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return bExists

    def restoreIndex(self):
        try:
            strFileName = self.strDictSaveTime
            if os.path.exists(strFileName):
                self.dictFileStorage = json.load(open(strFileName, 'r'))
                if len(self.dictFileStorage) > 0:
                    rospy.loginfo("restore success from {0}".format(strFileName))
                    rospy.logdebug("file:{0}, content:{1}".format(strFileName, json.dumps(self.dictFileStorage)))
            else:
                rospy.loginfo("break point not exists: {0}".format(strFileName))
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def checkLocalCacheEffect(self, strTargetFileName):
        bCacheEffect = False
        try:
            if (os.path.exists(strTargetFileName) == True) and (
                    self.dictFileStorage.has_key(strTargetFileName) == True):
                ## enter compare  modify timestamp
                intLocalCacheModifyTime = int(self.dictFileStorage[strTargetFileName]['modify_timestamp'])
                intLocalTargetTimeStamp = int(os.path.getmtime(strTargetFileName))
                if intLocalCacheModifyTime == intLocalTargetTimeStamp:
                    bCacheEffect = True
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return bCacheEffect

    def selectVersion(self, strTargetFileName, strRemoteMd5, intRemotePublishTime):
        EVersion = EnumVersion.INIT_VERSION
        try:
            while True:
                if not os.path.exists(strTargetFileName):
                    EVersion = EnumVersion.REMOTE_VERSION
                    rospy.loginfo(
                        "strTargetFileName:{0} not exists , EnumVersion.REMOTE_VERSION".format(strTargetFileName))
                    break
                if (os.path.exists(strTargetFileName) == True) and (
                        self.dictFileStorage.has_key(strTargetFileName) == False):
                    EVersion = EnumVersion.REMOTE_VERSION
                    rospy.loginfo(
                        "strTargetFileName:{0} not exists , EnumVersion.REMOTE_VERSION".format(strTargetFileName))
                    break
                if (os.path.exists(strTargetFileName) == True) and (
                        self.dictFileStorage.has_key(strTargetFileName) == True):
                    while True:
                        if not self.checkLocalCacheEffect(strTargetFileName):
                            rospy.loginfo(
                                "strTargetFileName:{0} modify_time  dis match cache_modify_time".format(
                                    strTargetFileName))
                            intLocalLastModifyTime = int(os.path.getmtime(strTargetFileName))
                            while True:
                                if intLocalLastModifyTime > intRemotePublishTime:
                                    rospy.loginfo(
                                        "===== may be develop modify  strTargetFileName:{0}  compare modify time and pubtime, local".format(
                                            strTargetFileName))
                                    EVersion = EnumVersion.LOCAL_VERSION
                                    break
                                if intLocalLastModifyTime < intRemotePublishTime:
                                    rospy.loginfo(
                                        "strTargetFileName:{0}  compare modify time and pubtime, remote".format(
                                            strTargetFileName))
                                    EVersion = EnumVersion.REMOTE_VERSION
                                    break
                                if intLocalLastModifyTime == intRemotePublishTime:
                                    rospy.loginfo(
                                        "strTargetFileName:{0}  compare modify time and pubtime, remote".format(
                                            strTargetFileName))
                                    EVersion = EnumVersion.REMOTE_VERSION
                                    break
                                break
                            break
                        if self.checkLocalCacheEffect(strTargetFileName):
                            rospy.loginfo(
                                "strTargetFileName:{0} modify_time match cache_modify_time".format(strTargetFileName))
                            ## compare md5
                            if strRemoteMd5 == self.dictFileStorage[strTargetFileName]['md5']:
                                EVersion = EnumVersion.LOCAL_VERSION
                                rospy.loginfo("strTargetFileName:{0} md5 match , EnumVersion.LOCAL_VERSION".format(
                                    strTargetFileName))
                            else:
                                EVersion = EnumVersion.REMOTE_VERSION
                                rospy.loginfo(
                                    "strTargetFileName:{0} md5 dis match  , EnumVersion.REMOTE_VERSION".format(
                                        strTargetFileName))
                            break
                        break
                    break
                break
            rospy.loginfo("EVersion:{0}".format(EVersion))
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return EVersion
