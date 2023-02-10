#!/usr/bin/env python
import traceback
from enum import Enum

import rospy


class EnumTrajResult(Enum):
    ENUMTRAJRESULT_V250_DOWNLOAD_SUCCESS = 0
    ENUMTRAJRESULT_V250_DOWNLOAD_FAILED = 1
    ENUMTRAJRESULT_V250_TRAJ_WARNING = 2

    ENUMTRAJRESULT_V260_DOWNLOAD_SUCCESS = 3
    ENUMTRAJRESULT_V260_DOWNLOAD_FAILED = 4
    ENUMTRAJRESULT_V260_TRAJ_WARNING = 5

    ENUMTRAJRESULT_V250_SEARCH_LAT_LON_SUCCESS = 6
    ENUMTRAJRESULT_V260_SEARCH_LAT_LON_SUCCESS = 7

    ENUMTRAJRESULT_V250_SEARCH_LAT_LON_FAILED = 8
    ENUMTRAJRESULT_V260_SEARCH_LAT_LON_FAILED = 9


class TrajResultTranTool:
    def __init__(self):
        pass

    def initData(self, enumValue):
        intValue = 1
        rospy.loginfo("initData:{0}".format(enumValue))
        try:
            while True:
                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V250_DOWNLOAD_SUCCESS:
                    intValue = 0
                    break
                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V250_DOWNLOAD_FAILED:
                    intValue = 1
                    break
                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V250_TRAJ_WARNING:
                    intValue = 2
                    break
                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_SUCCESS:
                    intValue = 3
                    break
                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V260_DOWNLOAD_FAILED:
                    intValue = 4
                    break

                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V260_TRAJ_WARNING:
                    intValue = 5
                    break

                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V250_SEARCH_LAT_LON_SUCCESS:
                    intValue = 6
                    break

                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V260_SEARCH_LAT_LON_SUCCESS:
                    intValue = 7
                    break

                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V250_SEARCH_LAT_LON_FAILED:
                    intValue = 8
                    break

                if enumValue == EnumTrajResult.ENUMTRAJRESULT_V260_SEARCH_LAT_LON_FAILED:
                    intValue = 9
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intValue