#!/usr/bin/env python
import hashlib
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
            # f.close()
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
            print "########################### instanceJobItem.strUrl:{0}".format(instanceJobItem.strUrl)

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
        print("compareJobVersion refJob[0].len:{0}".format(len(refJob[0].listJobCollect)))
        print("compareJobVersion len(refJob) :{0}".format(len(refJob)))
        print("compareJobVersion refJob[0] first url :{0}".format(len(refJob[0].listJobCollect[0].strUrl)))
        print("===========type(refJob[0].listJobCollect[0]):{0}".format(type(refJob[0].listJobCollect[0])))
        try:
            rospy.loginfo("*********AAAAAAAAAAAAAAAAAAAAAa*********** len(refJob[0].listJobCollect):{0}".format(
                len(refJob[0].listJobCollect)))
            for idx in range(0, len(refJob[0].listJobCollect)):
                print "****len:{0}".format(len(refJob[0].listJobCollect))
                print "****process idx : {0}".format(idx)
                instanceEnumVersion = self.compareJobItemVersion(refJob[0].listJobCollect[idx], instanceCacheUtils)
                refJob[0].listJobCollect[idx].eVersion = instanceEnumVersion
                #remote version push to refJob[0].listJobCollectUpdate
                if refJob[0].listJobCollect[idx].eVersion == EnumVersion.REMOTE_VERSION:
                    refJob[0].listJobCollectUpdate.append(refJob[0].listJobCollect[idx])
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

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
