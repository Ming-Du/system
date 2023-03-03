#!/usr/bin/env python
import os.path
import traceback

import psutil
import rospy


class ProcessUtil:
    intPid = None

    def __init__(self, intPid):
        self.intPid = intPid

    def getProcessStatus(self):
        intProcessExists = 1
        strProcessStatus = ""
        strPidFolder = "/proc/{0}".format(self.intPid)
        try:
            if os.path.exists(strPidFolder):
                psObject = psutil.Process(self.intPid)
                strProcessStatus = psObject.status()
                intProcessExists = 1
            else:
                intProcessExists = 0
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intProcessExists, strProcessStatus
