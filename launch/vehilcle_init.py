#!/usr/bin/env python
#--coding:utf-8
import json
import os
import traceback
import urllib2


def get_plate():
    plate = ""
    brand = ""
    try:
        with open("/home/mogo/data/vehicle_monitor/vehicle_config.txt") as fp2:
            contents2 = fp2.read().split("\n")

        plate = contents2[0].split(":")[-1]
        plate = plate.strip().strip("\"")

        brand = contents2[1].split(":")[-1]
        brand = brand.strip().strip("\"")
    except Exception as e:
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():';
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    return plate


def get_vehicle_purpose():
    vehicle_type=0
    dictVehicleInfo = {}
    strCar = get_plate()
    strUse = ""
    print "strCar:{0}".format(strCar)
    # dictTemp={}
    strUrl = "https://mygateway.zhidaozhixing.com/cmdbapi/car/selectCarBySn?vehicle_conf_sn={0}".format(strCar)
    headers = {'access_token': 'c4a2f30cebf64972bcd11577e1c07f86'}
    try:
        request = urllib2.Request(strUrl, headers=headers)
        response = urllib2.urlopen(request)
        content = response.read()
        dictContent = None
        if len(content) > 0:
            print json.loads(content)
            dictContent = json.loads(content)
            if dictContent.has_key('data'):
                while True:
                    if dictContent['data'] == u"开发":
                        strUse = "develop"
                        vehicle_type=1
                        break
                    if dictContent['data'] == u"测试":
                        strUse = "test"
                        vehicle_type=2
                        break
                    if dictContent['data'] == u"演示":
                        strUse = "demonstration"
                        vehicle_type=3
                        break
                    if dictContent['data'] == u"运营":
                        strUse = "production"
                        vehicle_type=4
                        break
                    print "unknow"
                    break
            else:
                strUse = "unknow"
        if len(strCar) > 0 and len(strUse) > 0:
            dictUse = {}
            dictUse['sn'] = strCar
            dictUse['use'] = strUse
            if os.path.exists("/home/mogo/data/vehicle_use.info"):
                os.remove("/home/mogo/data/vehicle_use.info")
            with open('/home/mogo/data/vehicle_use.info', 'wa+') as f:
                f.write(json.dumps(dictUse))
                f.write("\n")

    except Exception as e:
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():';
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    return vehicle_type


if __name__ == "__main__":
    exit(get_vehicle_purpose())
