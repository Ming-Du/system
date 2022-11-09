#!/usr/bin/env python

import rospy
import traceback
import commands


class CommonPara:
    dictCarInfo = None

    def __init__(self):
        self.dictCarInfo = {}

    def read_car_info(self):
        try:
            dictCarInfo = {}
            with open("/home/mogo/data/vehicle_monitor/vehicle_config.txt") as fp2:
                contents2 = fp2.read().split("\n")

            plate = contents2[0].split(":")[-1]
            plate = plate.strip().strip("\"")

            brand = contents2[1].split(":")[-1]
            brand = brand.strip().strip("\"")

            dictCarInfo["car_plate"] = plate
            dictCarInfo["car_type"] = brand
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return dictCarInfo

    def getMac(self):
        try:
            strCmd = "ifconfig eth0 | grep ether | awk '{print $2}'"
            status, output = commands.getstatusoutput(strCmd)
            rospy.logdebug("----------------status:{0},output:{1}".format(status, output))
            if status == 0:
                self.dictCarInfo['mac'] = str(output)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def initPara(self):
        try:
            self.dictCarInfo = self.read_car_info()
            self.getMac()
            rospy.logdebug("internal CommonPara: {0}".format(self.dictCarInfo))
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
