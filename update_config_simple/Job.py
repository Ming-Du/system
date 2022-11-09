#!/usr/bin/env python
import logging
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
        pass

    def setCurrentTimeStamp(self):
        pass

    def getCurrentTimeStamp(self):
        return self.intJobCtime

    def handlerDataSource(self,dataSource):
        self.handlerDataSource = dataSource
