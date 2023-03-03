#!/usr/bin/env python
import logging
import os
import traceback

import rospy

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d]' '- %(levelname)s: %(message)s',level=logging.INFO)
logging.debug('debug message')
from EnumJobType import EnumJobType
from JobItem import JobItem
from EnumJobStatus import EnumJobStatus


class Job:
    strJobId = None
    listJobCollect = None
    enumStatus = None
    intPid = None
    enumReplaceSelect = None
    intJobCtime = None
    enumJobType = None
    handlerDataSource = None
    listJobCollectUpdate = None
    mStrJobFeature = None
    strDownTempFolder = None
    strTaskListFile = None

    def __init__(self):
        self.strJobId = ""
        self.listJobCollect = []
        self.enumStatus = EnumJobStatus.JOB_STATUS_INIT
        self.intPid = 0
        self.enumReplaceSelect = 0
        self.intJobCtime = 0
        self.enumJobType = EnumJobType.JOB_TYPE_INIT
        self.handlerDataSource = None
        self.listJobCollectUpdate = []
        self.mStrJobFeature = ""
        self.strDownTempFolder = ""
        self.strTaskListFile = ""
        pass

    def setCurrentTimeStamp(self):
        pass

    def getCurrentTimeStamp(self):
        return self.intJobCtime

    def handlerDataSource(self,dataSource):
        self.handlerDataSource = dataSource

    def setStrJobFeature(self, strModuleName, intPublishTime):
        self.mStrJobFeature = "{0}_{1}".format(strModuleName, intPublishTime)
        self.createFeatureFolder()
        self.strTaskListFile = "{0}/task.list".format(self.strDownTempFolder)

    def createFeatureFolder(self):
        try:
            self.strDownTempFolder = "/home/mogo/data/update_config_temp/{0}".format(self.mStrJobFeature)
            if os.path.exists(self.strDownTempFolder):
                pass
            else:
                os.makedirs(self.strDownTempFolder)
                os.chmod(self.strDownTempFolder, 0777)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
