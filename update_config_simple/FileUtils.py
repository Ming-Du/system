#!/usr/bin/env python
import os
import traceback

import rospy


class FileUtils:
    def __init__(self):
        pass

    def linkFileSimple(self, strDownStageLocationFileMap, strStandardLocationFileMap):
        rospy.loginfo("linkFileSimple:link_name:{0},target_name:{1}".format(strStandardLocationFileMap,strDownStageLocationFileMap))
        ret = 0
        try:
            if os.path.exists(strDownStageLocationFileMap):
                while True:
                    if (os.path.exists(strStandardLocationFileMap)) and (
                            os.readlink(strStandardLocationFileMap) == strDownStageLocationFileMap):
                        rospy.loginfo("############ link file:{0}  and target_file:{1} name normal".format(
                            strStandardLocationFileMap, strDownStageLocationFileMap))
                        break
                    if (os.path.exists(strStandardLocationFileMap)) and (
                            os.readlink(strStandardLocationFileMap) != strDownStageLocationFileMap):
                        rospy.loginfo("############ link file:{0}  and target_file:{1} name abnormal".format(
                            strStandardLocationFileMap, strDownStageLocationFileMap))
                        os.remove(strStandardLocationFileMap)
                        os.symlink(strDownStageLocationFileMap, strStandardLocationFileMap)
                        ret = 1
                        break
                    if not os.path.exists(strStandardLocationFileMap):
                        rospy.loginfo("link file: {0} not exists ,now create ".format(strStandardLocationFileMap))
                        os.symlink(strDownStageLocationFileMap, strStandardLocationFileMap)
                        ret = 1
                        break
                    break
            else:
                rospy.logwarn("src file:{0} not exists, link failed".format(strDownStageLocationFileMap))
                ret = -1

        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return ret

    def linkFileAccordConfig(self, strLinkConfigPath):
        rospy.loginfo("now link config name:{0}".format(strLinkConfigPath))
        listContent = None
        try:
            while True:
                if not os.path.exists(strLinkConfigPath):
                    break
                if os.path.exists(strLinkConfigPath):
                    with open(strLinkConfigPath, "r") as f:
                        strContent = f.read()
                        rospy.loginfo("strContent:{0}".format(strContent))
                        listContent = strContent.splitlines()
                    break
                break
            ##check listConten
            listUnit = None

            if listContent is not None:
                for idx in range(len(listContent)):
                    listUnit = None
                    if len(listContent[idx]) > 0:
                        listUnit = str(listContent[idx]).split(':')
                        if listUnit is not None:
                            strSrcPath = listUnit[0].strip()
                            strLinkPath = listUnit[1].strip()
                            self.linkFileSimple(strSrcPath, strLinkPath)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))