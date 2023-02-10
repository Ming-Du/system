#!/usr/bin/env python
import base64
import hashlib
import json
import os
import time
import traceback

import rospy

from JobItem import JobItem
from EnumVersion import EnumVersion
from CacheUtils import CacheUtils
from Job import Job


def checkFileMd5(strFileName):
    strFileMd5Value = ""
    try:
        if not os.path.exists(strFileName):
            return strFileMd5Value
        with open(strFileName, 'rb') as f:
            strFileMd5Value = str(hashlib.md5(f.read()).hexdigest())
        rospy.logdebug("checkFileMd5: fileName:{0}, strFileMd5Value:{1}".format(strFileName, strFileMd5Value))
    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
    return strFileMd5Value


class CommonUtilsCompare:
    def __init__(self):
        pass

    def compareJobItemVersion(self, instanceJobItem, instanceCacheUtils):
        try:
            rospy.logdebug("typeof(instanceJobItem):{0}".format(instanceJobItem))
            rospy.logdebug("compareJobItemVersion:{0}".format(instanceJobItem))
            strTargetFileName = instanceJobItem.strFullFileName
            strRemoteMd5 = instanceJobItem.strMd5
            intRemotePublishTime = instanceJobItem.intPublishTimeStamp
            instanceJobItem.eVersion = instanceCacheUtils.selectVersion(strTargetFileName, strRemoteMd5,
                                                                        intRemotePublishTime)

            strDirName = os.path.dirname(strTargetFileName)
            rospy.logdebug("=====strDirName:{0}".format(strDirName))

            strBaseName = os.path.basename(strTargetFileName)
            rospy.logdebug("=======strBaseName:{0}".format(strBaseName))

            ## check strTempTargetFileNameFolder exists
            strTempTargetFileName = "/home/mogo/data/config_backup/{0}/{1}".format(strDirName, strBaseName)
            strTempTargetFileNameFolder = os.path.dirname(strTempTargetFileName)
            rospy.logdebug("=========== strTempTargetFileName:{0}".format(strTempTargetFileName))
            rospy.logdebug("=========== strTempTargetFileNameFolder:{0}".format(strTempTargetFileNameFolder))

            if not os.path.exists(strTempTargetFileNameFolder):
                os.makedirs(strTempTargetFileNameFolder)
                os.chmod(strTempTargetFileNameFolder, 0777)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return instanceJobItem.eVersion

    def compareJobVersion(self, refJob, instanceCacheUtils):
        try:
            for idx in range(0, len(refJob[0].listJobCollect)):
                instanceEnumVersion = self.compareJobItemVersion(refJob[0].listJobCollect[idx], instanceCacheUtils)
                refJob[0].listJobCollect[idx].eVersion = instanceEnumVersion
                #remote version push to refJob[0].listJobCollectUpdate
                if refJob[0].listJobCollect[idx].eVersion == EnumVersion.REMOTE_VERSION:
                    refJob[0].listJobCollectUpdate.append(refJob[0].listJobCollect[idx])
        except Exception as e:
            print('repr(e):{0}'.format(repr(e)))
            print('e.message:{0}'.format(e.message))
            print('traceback.format_exc():%s' % (traceback.format_exc()))

    def checkFileMd5(self,strFileName):
        strFileMd5Value = ""
        try:
            if not os.path.exists(strFileName):
                return strFileMd5Value
            with open(strFileName, 'rb') as f:
                strFileMd5Value = str(hashlib.md5(f.read()).hexdigest())
            rospy.logdebug("checkFileMd5: fileName:{0}, strFileMd5Value:{1}".format(strFileName, strFileMd5Value))
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return strFileMd5Value

    def fromBase64Restore(self, strInputBase64FileName, strOutputFilePath):
        rospy.loginfo("CommonUtilsCompare::fromBase64Restore strInputBase64FileName:{0},strOutputFilePath:{1}".format(strInputBase64FileName,strOutputFilePath))
        ret = 0
        intErrno = 0
        strBase64Content = ""
        try:
            while True:
                if not os.path.exists(strInputBase64FileName):
                    ret = -1
                    break
                with open(strInputBase64FileName, "r") as f:
                    content = f.read()
                if len(content) == 0:
                    ret = -1
                    break
                if len(content) > 0:
                    dictContent = json.loads(content)
                    if dictContent.has_key('errno'):
                        intErrno = int(dictContent['errno'])
                    if (intErrno == 0) and (dictContent.has_key('result')):
                        strBase64Content = str(dictContent['result'])
                if len(strBase64Content) == 0:
                    ret = -1
                    break

                if len(strBase64Content) > 0:
                    strOriginContent = base64.b64decode(strBase64Content)
                    if os.path.exists(strOutputFilePath):
                        os.remove(strOutputFilePath)
                    with open(strOutputFilePath, 'ab+') as f:
                        f.write(strOriginContent)
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            ret = -1
        if os.path.exists(strOutputFilePath):
            ret = 0
        else:
            ret = -1
        return ret, strOutputFilePath
