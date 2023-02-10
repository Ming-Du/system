#!/usr/bin/env python
import os
import shutil
import traceback

import rospy
from CommonUtilsCompare import CommonUtilsCompare

instanceCommonUtilsCompare = CommonUtilsCompare()


class CommonDataSourceUtil:
    def __init__(self):
        pass

    def checkAtomicFeature(self, refJob):
        rospy.loginfo("enter CommonDataSourceUtil::checkAtomicFeature")
        try:
            for idx in range(len(refJob.listJobCollectUpdate)):
                rospy.logwarn("process file:{0}".format(refJob.listJobCollectUpdate[idx].strFullFileTempName))
                if not os.path.exists(refJob.listJobCollectUpdate[idx].strFullFileTempName):
                    rospy.logwarn("AiModelImpInterfaceDataSource::checkAtomicFeature tempFileNotExists:{0}".format(
                        refJob.listJobCollectUpdate[idx].strFullFileTempName))
                    refJob.listJobCollectUpdate[idx].intStatus = -1
                    continue
                strStandardMd5 = refJob.listJobCollectUpdate[idx].strMd5
                strTempFile = refJob.listJobCollectUpdate[idx].strFullFileTempName
                strRealMd5 = instanceCommonUtilsCompare.checkFileMd5(strTempFile)
                rospy.logwarn(
                    "CommonDataSourceUtil::checkAtomicFeature strStandardMd5:{0},realfile:{1}_strRealMd5:{2}".format(
                        strStandardMd5, strTempFile, strRealMd5))
                if strRealMd5 == strStandardMd5:
                    refJob.listJobCollectUpdate[idx].intStatus = 0
                    rospy.logwarn(
                        "CommonDataSourceUtil::checkAtomicFeature strFileName:{0} matched md5".format(
                            strTempFile))
                if strRealMd5 != strStandardMd5:
                    refJob.listJobCollectUpdate[idx].intStatus = -1
                    rospy.logwarn(
                        "CommonDataSourceUtil::checkAtomicFeature strFileName:{0} not  matched md5".format(
                            strTempFile))

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def install_dst_path(self, refJob):
        try:
            for idx in range(len(refJob.listJobCollectUpdate)):
                if os.path.exists(refJob.listJobCollectUpdate[idx].strFullFileTempName) and refJob.listJobCollectUpdate[idx].intStatus == 0:
                    strDestFolderName = os.path.dirname(refJob.listJobCollectUpdate[idx].strFullFileName)
                    if not os.path.exists(strDestFolderName):
                        os.makedirs(strDestFolderName)
                        os.chmod(strDestFolderName,0777)
                    shutil.copyfile(refJob.listJobCollectUpdate[idx].strFullFileTempName,
                                    refJob.listJobCollectUpdate[idx].strFullFileName)
                    rospy.loginfo(
                        "SUCCESS CommonDataSourceUtil::install_dst_path success process file:{0}".format(refJob.listJobCollectUpdate[
                            idx].strFullFileTempName))

                else:
                    rospy.loginfo(
                        "FAIL CommonDataSourceUtil::install_dst_path  failed process file:{0}".format(refJob.listJobCollectUpdate[
                            idx].strFullFileTempName))
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def clear_slam_folder(self, refJob):
        intSuccessNum = 0
        try:
            for idx in range(len(refJob.listJobCollectUpdate)):
                if os.path.exists(refJob.listJobCollectUpdate[idx].strFullFileTempName) and refJob.listJobCollectUpdate[idx].intStatus == 0:
                    intSuccessNum = intSuccessNum + 1
            if intSuccessNum == len(refJob.listJobCollectUpdate) and intSuccessNum > 0:
                for idx in range(len(refJob.listJobCollectUpdate)):
                    strDestFolderName = os.path.dirname(refJob.listJobCollectUpdate[idx].strFullFileName)
                    if not os.path.exists(strDestFolderName):
                        os.makedirs(strDestFolderName)
                        os.chmod(strDestFolderName,0777)
                    if os.path.exists(strDestFolderName):
                        del_list = os.listdir(strDestFolderName)
                        for f in del_list:
                            file_path = os.path.join(strDestFolderName, f)
                            if os.path.isfile(file_path):
                                rospy.loginfo("CommonDataSourceUtil::clear_slam_folder remove file:{0}".format(file_path))
                                os.remove(file_path)
            else:
                rospy.logwarn("CommonDataSourceUtil::clear_slam_folder intSuccessNum:{0},"
                              "len(refJob.listJobCollectUpdate):{0}".format(intSuccessNum,
                                                                            len(refJob.listJobCollectUpdate)))

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))