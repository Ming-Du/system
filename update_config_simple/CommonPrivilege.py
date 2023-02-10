#!/usr/bin/env python
# -*- coding: utf-8 -*-
import commands
import traceback

import rospy
from entity.GenLaunchList import GenLaunchList

from enum import Enum


class EnumPrivilegeCheck(Enum):
    PRIVILEGE_CHECK_DENY = 0
    PRIVILEGE_CHECK_ALLOW = 1
    PRIVILEGE_CHECK_UNKNOW = 2


class CommonPrivilege:
    instanceGenLaunchList = None
    strXiverType = None
    strCarType = None
    strHostName = None
    dictContent = None
    enumPri = None

    def __init__(self):
        self.dictContent = {}
        self.loadConfig()

        pass

    def loadConfig(self):
        try:
            self.instanceGenLaunchList = GenLaunchList()
            self.strXiverType = self.instanceGenLaunchList.getXiverType()
            self.strCarType = self.instanceGenLaunchList.getCarType()
            self.strHostName = self.instanceGenLaunchList.getHostName()
            self.instanceGenLaunchList.initData()
            self.dictContent = self.instanceGenLaunchList.dictContent
            rospy.loginfo("strXiverType:{0}".format(self.strXiverType))
            rospy.loginfo("strCarType:{0}".format(self.strCarType))
            rospy.loginfo("strHostName:{0}".format(self.strHostName))

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def getModuleAllow(self, strPackageName, strName):
        rospy.loginfo("strPackageName:{0},strName:{1}".format(strPackageName, strName))
        enumCheckResult = EnumPrivilegeCheck.PRIVILEGE_CHECK_UNKNOW
        try:
            intFileListLen = len(self.dictContent['file_list'])
            dictFileList = self.dictContent['file_list']
            for idx in range(intFileListLen):
                dictSub = dictFileList[idx]

                if dictSub['name'] == strName and dictSub['package'] == strPackageName:

                    listXivers = dictSub['machine'][self.strCarType][self.strXiverType]

                    if self.strHostName in listXivers:
                        enumCheckResult = EnumPrivilegeCheck.PRIVILEGE_CHECK_ALLOW
                    else:
                        enumCheckResult = EnumPrivilegeCheck.PRIVILEGE_CHECK_DENY
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        rospy.loginfo("enumCheckResult:{0}".format(enumCheckResult))
        self.enumPri = enumCheckResult
        return enumCheckResult
