#!/usr/bin/env python
import traceback
from urllib import unquote

import rospy
import Job


class CommonWgetFileRestore:
    def __init__(self):
        pass

    def processSingleFile(self, strJobFolderPath, strUrl):
        strLastName = ""
        intRet = -1
        rospy.logdebug("func CommonWgetFileRestore::processSingleFile   strJobFolderPath:{0}".format(strJobFolderPath))
        rospy.logdebug("func CommonWgetFileRestore::processSingleFile   strUrl:{0}".format(strUrl))
        try:
            while True:
                if len(strJobFolderPath) == 0:
                    intRet = -1
                    break
                if len(strUrl) == 0:
                    intRet = -1
                    break
                strDecodeUrl = unquote(strUrl)
                listUrlContent = strDecodeUrl.split('/')
                if len(listUrlContent) > 2:
                    strBaseFileName = listUrlContent[len(listUrlContent) - 1]
                    strLastName = "{0}/{1}".format(strJobFolderPath, strBaseFileName)
                    intRet = 0
                    rospy.logdebug("=========== strLastName:{0}".format(strLastName))
                break

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return strLastName

    def processJob(self, refJob):

        pass
