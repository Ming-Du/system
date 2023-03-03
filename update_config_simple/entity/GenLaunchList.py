import commands
import json
import traceback
from CommonPara import CommonPara
import os
import rospy


class GenLaunchList:
    globalCommonPara = None
    strTempLaunchListFolder = ""
    dictHostNameMapList = {}
    dictContent = None

    def __init__(self):
        self.globalCommonPara = CommonPara()
        self.globalCommonPara.initPara()
        self.strTempLaunchListFolder = "/tmp/monitor_process/"
        self.dictContent = {}

    def getXiverType(self):
        XiverType = "6x"
        if os.path.exists("/etc/hosts"):
            strCmdCheckMultiXiver = "cat  /etc/hosts | grep slave | wc -l"
            try:
                (status, output) = commands.getstatusoutput(strCmdCheckMultiXiver)
                if status == 0:
                    rospy.logdebug("output:{0}".format(output))
                    while True:
                        if int(output) == 1:
                            XiverType = "2x"
                            break

                        if int(output) == 0:
                            XiverType = "1x"
                            break

                        if int(output) > 1:
                            XiverType = "6x"
                            break
                        break
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        rospy.logdebug("XiverType:{0}".format(XiverType))
        return XiverType

    def getCarType(self):
        strCarType = "jinlv"
        try:
            while True:

                strCarType = self.globalCommonPara.dictCarInfo['car_type']
                if str(self.globalCommonPara.dictCarInfo['car_type']) == "DF":
                    strCarType = "df"
                    break
                if str(self.globalCommonPara.dictCarInfo['car_type']) == "JINLV":
                    strCarType = "jinlv"
                    break
                if str(self.globalCommonPara.dictCarInfo['car_type']) == "HQ":
                    strCarType = "hq"
                    break
                if str(self.globalCommonPara.dictCarInfo['car_type']) == "FT":
                    strCarType = "sweeper"
                    break
                if str(self.globalCommonPara.dictCarInfo['car_type']) == "KW":
                    strCarType = "kaiwo"
                    break
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        rospy.logdebug("strCarType:{0}".format(strCarType))
        return strCarType

    def initData(self):
        strCarType = self.getCarType()
        strXiverType = self.getXiverType()
        dictContent = None
        dictNodeList = None
        fileLength = 0
        strFileName = "/home/mogo/autopilot/share/launch/config/launch_config.json"
        strContent = None
        try:
            with open(strFileName, "r") as f:
                strContent = f.read()
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

        try:
            self.dictContent = json.loads(strContent)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def getHostName(self):
        strHostName = ""
        try:
            strCmd = "ifconfig  eth0   | grep inet |  grep netmask | awk '{print $2}'"
            (status, output) = commands.getstatusoutput(strCmd)
            rospy.logdebug("status:%d,output:%s" % (status, output))
            strIp = output

            strCmd2 = "cat /etc/hosts |  grep '%s' | awk '{print $2}' | head -n 1" % (strIp)
            (status, output) = commands.getstatusoutput(strCmd2)
            if status == 0 and len(output) > 0:
                strHostName = output
            rospy.logdebug("status:%d,output:%s" % (status, strHostName))
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return strHostName
