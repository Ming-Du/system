#!/usr/bin/env python
import traceback

import rospy


import json
import os


class CommonUtilsReadFile:

    def __init__(self):
        pass

    def readJsonConfig(self, strConfigFilePath):
        intError = 0
        strFileContent = ""
        dictConfig = {}
        try:
            while True:
                if not os.path.exists(strConfigFilePath):
                    intError = -1
                    break
                if os.path.exists(strConfigFilePath):
                    fileObject = open(strConfigFilePath, "r")
                    try:
                        strFileContent = fileObject.read()
                    except Exception as e:
                        rospy.logwarn(str(e))
                    finally:
                        fileObject.close()
                    if len(strFileContent) > 0:
                        dictConfig = json.loads(strFileContent)
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intError, dictConfig
