#!/usr/bin/env python
import sys
import os
import traceback

import rospy

sys.path.append(os.path.dirname(__file__) + '/../mogo_reporter/script/')
sys.path.append('../mogo_reporter/script/')
from get_msg_by_code import gen_report_msg


class CommonEventUtils:
    def __init__(self):
        pass

    def SaveEventToFile(self, strFileName, code, strSrcApp, strEventMsg):
        rospy.logdebug("enter SaveEventToFile")
        json_msg = ""
        try:
            json_msg = gen_report_msg(strFileName, code,strSrcApp,strEventMsg)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        rospy.logdebug("event json_msg:{0}".format(json_msg))
        try:
            with open("/home/mogo/data/log/msg_log/system_master_report.json", 'a+') as fp:
                fp.write(json_msg + '\n')
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
