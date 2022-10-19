#!/usr/bin/env python
import logging

import rospy

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d]' '- %(levelname)s: %(message)s',level=logging.INFO)
logging.debug('debug message')
import json
import traceback
from io import StringIO

from CommonPara import CommonPara
import pycurl
import StringIO
import sys
from enum import Enum


class CommonHttpUtils:
    def __init__(self):
        pass

    def sendSimpleHttpRequestWithHeader(self, strUrl, dictPostPara):
        intHttpCode = -1
        strRespContent = ""
        try:
            while True:
                if len(strUrl) == 0:
                    break
                if len(dictPostPara) == 0:
                    break
                rospy.loginfo("sendSimpleHttpRequestWithHeader strUrl:{0},dictPostPara:{1}".format(strUrl, dictPostPara))
                url = strUrl
                crl = None
                crl = pycurl.Curl()
                crl.setopt(pycurl.VERBOSE, 0)
                crl.setopt(pycurl.FOLLOWLOCATION, 1)
                crl.setopt(pycurl.MAXREDIRS, 5)
                crl.setopt(pycurl.CONNECTTIMEOUT, 5)
                crl.setopt(pycurl.TIMEOUT, 300)
                crl.setopt(pycurl.HTTPPROXYTUNNEL, 1)
                crl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json', 'Accept: application/json'])
                crl.fp = StringIO.StringIO()
                if len(dictPostPara) > 0:
                    crl.setopt(pycurl.POSTFIELDS, json.dumps(dictPostPara))
                crl.setopt(pycurl.URL, url)
                crl.setopt(pycurl.WRITEFUNCTION, crl.fp.write)
                crl.perform()
                intHttpCode = int(crl.getinfo(pycurl.HTTP_CODE))
                rospy.loginfo("================  http  code:{0}".format(intHttpCode))
                if intHttpCode == 200:
                    strRespContent = crl.fp.getvalue()
                break
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
        return intHttpCode, strRespContent

