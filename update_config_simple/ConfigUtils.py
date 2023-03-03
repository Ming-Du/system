#!/usr/bin/env python
import json
import os.path
import traceback

import rospy


class ConfigUtils:

    dictContent = None
    intTraj260Priority = 0
    intTraj260LineIdEnableFlag = None
    intTraj260LonLatTypeEnableFlag = None
    intTraj250Priority = 0
    intTraj250LineIdEnableFlag = None
    intTraj250LonLatTypeEnableFlag = None

    def __init__(self):
        self.dictContent = {}
        self.intTraj260LineIdEnableFlag = 1
        self.intTraj260LonLatTypeEnableFlag = 0
        self.intTraj260Priority = 1
        self.intTraj250LineIdEnableFlag = 1
        self.intTraj250LonLatTypeEnableFlag = 0
        self.intTraj250Priority = 0

    def debug(self):
        rospy.loginfo("self.intTraj260LineIdEnableFlag:{0}".format(self.intTraj260LineIdEnableFlag))
        rospy.loginfo("self.intTraj260LonLatTypeEnableFlag:{0}".format(self.intTraj260LonLatTypeEnableFlag))
        rospy.loginfo("self.intTraj260Priority:{0}".format(self.intTraj260Priority))
        rospy.loginfo("self.intTraj250LineIdEnableFlag:{0}".format(self.intTraj250LineIdEnableFlag))
        rospy.loginfo("self.intTraj250LonLatTypeEnableFlag:{0}".format(self.intTraj250LonLatTypeEnableFlag))
        rospy.loginfo("self.intTraj250Priority:{0}".format(self.intTraj250Priority))


    def initConfig(self, strConfigFileName):
        rospy.loginfo("traj strConfigFileName:{0}".format(strConfigFileName))
        ret = 0
        try:
            if os.path.exists(strConfigFileName):
                with open(strConfigFileName) as f:
                    strContent = f.read()
                    if len(strContent) > 0:
                        self.dictContent = json.loads(strContent)
                    else:
                        ret = -1
            else:
                ret = -1
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        self.setStatus()
        return ret

    def setStatus(self):
        ret = 0
        try:
            if len(self.dictContent) > 0:
                self.intTraj260Priority = int(self.dictContent['260_traj']['priority'])
                self.intTraj260LineIdEnableFlag = int(self.dictContent['260_traj']['line_id_type_enable'])
                self.intTraj260LonLatTypeEnableFlag = int(self.dictContent['260_traj']['local_lon_lat_type_enable'])
                self.intTraj250Priority = int(self.dictContent['250_traj']['priority'])
                self.intTraj250LineIdEnableFlag = int(self.dictContent['250_traj']['line_id_type_enable'])
                self.intTraj250LonLatTypeEnableFlag = int(self.dictContent['250_traj']['local_lon_lat_type_enable'])
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return ret
