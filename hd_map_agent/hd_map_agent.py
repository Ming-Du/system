#!/usr/bin/env python
import traceback
import commands
import os
import time

times = 0
while True:
    times = times + 1
    strFlagFile = "/home/mogo/autopilot/share/hd_map_agent/ready.flag"
    if os.path.exists(strFlagFile):
        break
    if not os.path.exists(strFlagFile):
        strCmd = "sudo apt-get update  &&  sudo apt-get  install -y python-requests  && sudo apt-get install -y python-psutil "
        status, output = commands.getstatusoutput(strCmd)
        print "===================================================================status:{0},output:{1}".format(status,
                                                                                                                output)
        if status == 0:
            strTouchCmd = "touch  {0}".format(strFlagFile)
            os.system(strTouchCmd)
            if os.path.exists(strFlagFile):
                break
    print "===================== install package recycle times:{0}".format(times)
    time.sleep(5)
print "success break while"

import subprocess

import psutil
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import base64
import collections
import json
import traceback
# import os
import shutil
import hashlib
import urllib2

import thread
import threading

from random import random

import rospy
import rosnode
import rosparam
import os
from threading import Thread

import std_msgs
from std_msgs.msg import String
from rospy import init_node, Subscriber
import json
# import psutil
import collections
import sys
# import simplejson
import logging
import re
import time
import datetime
import rospy

from autopilot_msgs.msg import BinaryData
# import proto.mapectory_agent_sync_status_pb2 as common_mapectory_agent_sync_status_pb2
import proto.message_pad_pb2 as common_message_pad_pb2

from threading import Thread
import threading
from concurrent.futures import ThreadPoolExecutor
import json
import collections
import json
from os import path, access, R_OK
import os, sys, stat
import uuid

from sys import path
import os
import requests
import proto.localization_pb2 as common_localization
# import pycurl
import StringIO
import commands
import proto.vehicle_state_pb2 as common_vehicle_state_pb2

path.append(os.path.dirname(__file__) + '/../mogo_reporter/script/')
sys.path.append('../mogo_reporter/script/')
from get_msg_by_code import gen_report_msg

tree = lambda: collections.defaultdict(tree)

global_MaxTryTimes = 2

globalManagerProcessRequestPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Manager')
globalDownloadWorkerRequestPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='DownloadWorker')
globalControlCmdRequestPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ControlCmd')

globalPubToSystemMasterStatus = rospy.Publisher("/mapectory_agent/cmd/status", BinaryData, queue_size=1000)

globalDictTaskRunningStatus = {}

globalStrTempDownFolder = "/home/mogo/data/down_map_agent_tmp/"
globalStrStageDownFolder = "/home/mogo/data/down_map_agent_stage/"
globalMapPosition_longitude = 116.402544
globalMapPosition_latitude = 39.91405
globalStrPort = "443"

globalPilotMode = 0


class TaskManager:
    dictTaskInfo = None
    dictHandler = None

    def __init__(self):
        self.dictTaskInfo = {}
        self.dictHandler = {}
        pass

    def addTask(self, strTaskId):
        print "--------------- enter addTask"
        ret = True
        self.dictTaskInfo[strTaskId] = 1
        self.debugTaskInfo()
        return ret

    def addHandle(self, strTaskId, curlHandler):
        print "--------------- enter addHandle"
        ret = True
        self.dictHandler[strTaskId] = curlHandler
        self.debugTaskInfo()
        return ret

    def removeTask(self, strTaskId):
        print "--------------- enter removeTask"
        if self.dictTaskInfo.has_key(strTaskId):
            del self.dictTaskInfo[strTaskId]
        self.debugTaskInfo()

    def removeHandler(self, strTaskId):
        print "--------------- enter removeHandler"
        if self.dictHandler.has_key(strTaskId):
            del self.dictHandler[strTaskId]
        self.debugTaskInfo()

    def checkTaskExists(self, strTaskId):
        ret = True
        if self.dictTaskInfo.has_key(strTaskId):
            print "strTask is exists: {0}".format(strTaskId)
            ret = True
        else:
            print "strTask not exists :{0}".format(strTaskId)
            ret = False
        return ret

    def checkHandlerExists(self, strTaskId):
        ret = True
        if self.dictHandler.has_key(strTaskId):
            print "strTask is exists: {0}".format(strTaskId)
            ret = True
        else:
            print "strTask not exists :{0}".format(strTaskId)
            ret = False
        return ret

    def debugTaskInfo(self):
        print "current TaskInfo:{0}".format(json.dumps(self.dictTaskInfo))
        print "current HandleInfo:{0}".format(json.dumps(self.dictHandler))

    def delAllTask(self):
        print  "--------------- enter delAllTask"
        self.dictTaskInfo = {}
        self.debugTaskInfo()


class CommonPara:
    dictCarInfo = None

    def __init__(self):
        self.dictCarInfo = {}

    def read_car_info(self):
        dictCarInfo = {}
        try:
            with open("/autocar-code/project_commit.txt") as fp1:
                contents1 = fp1.read().split("\n")

            dictCarInfo["code_version"] = contents1[1][len("Version:"):]

            with open("/home/mogo/data/vehicle_monitor/vehicle_config.txt") as fp2:
                contents2 = fp2.read().split("\n")

            plate = contents2[0].split(":")[-1]
            plate = plate.strip().strip("\"")

            brand = contents2[1].split(":")[-1]
            brand = brand.strip().strip("\"")
            # plate = "HYDF2229"
            dictCarInfo["car_plate"] = plate
            dictCarInfo["car_type"] = brand
        except Exception as e:
            print("read carInfo failed!")
            return False
        # print(dictCarInfo)
        return dictCarInfo

    def initPara(self):
        self.dictCarInfo = self.read_car_info()


class CacheUtils:
    dictMapAgentRecord = None
    strDictSaveTime = None

    def __init__(self):
        self.dictMapAgentRecord = {}
        self.strDictSaveTime = "/home/mogo/data/map_agent_cache_record.json"
        self.restoreIndex()

    def WriteFileCacheInfo(self, lMapId, strMapUrl, strMapMd5, timestampMap, intModifyTime_Map):
        print "process WriteFileCacheInfo: lMapId:{0}, strMapUrl:{1}, strMapMd5:{2},timestampMap:{3},intModifyTime_Map:{4}".format(
            lMapId, strMapUrl, strMapMd5, timestampMap, intModifyTime_Map)
        try:
            mapDict = {}
            # stopDict = {}
            strMapName = "{0}".format(lMapId)
            print "strMapName:{0}".format(strMapName)
            mapDict['url'] = strMapUrl
            mapDict['timestamp'] = timestampMap
            mapDict['md5'] = strMapMd5
            mapDict['modify_time'] = intModifyTime_Map
            self.dictMapAgentRecord[strMapName] = mapDict

            print "=======================current dictMapAgentRecord:{0}".format(
                json.dumps(self.dictMapAgentRecord))

            # with open(self.strDictSaveTime, 'w') as f:
            #     json.dump(self.dictMapAgentRecord, f)
            #     print "flush file"
            #     f.close()
            json.dump(self.dictMapAgentRecord, open(self.strDictSaveTime, 'w'))


        except Exception as e:
            print "exception happend"
            print e.message
            print str(e)
            print 'str(Exception):\t', str(Exception)
            print 'str(e):\t\t', str(e)
            print 'repr(e):\t', repr(e)
            print 'e.message:\t', e.message
            print 'traceback.print_exc():'
            traceback.print_exc()
            print 'traceback.format_exc():\n%s' % (traceback.format_exc())

    def CheckMapFileCacheExists(self, lMapId, timestamp, strMapMd5):
        bExists = True
        try:
            strMapName = "{0}".format(lMapId)
            if self.dictMapAgentRecord.has_key(strMapName):
                bExists = True
            else:
                bExists = False
            print "CheckMapFileCacheExists check file:{0}, result:{1}".format(strMapName, bExists)
        except Exception as e:
            print "exception happend"
            print e.message
            print str(e)
            print 'str(Exception):\t', str(Exception)
            print 'str(e):\t\t', str(e)
            print 'repr(e):\t', repr(e)
            print 'e.message:\t', e.message
            print 'traceback.print_exc():'
            traceback.print_exc()
            print 'traceback.format_exc():\n%s' % (traceback.format_exc())
        return bExists

    def restoreIndex(self):
        try:
            strFileName = self.strDictSaveTime
            if os.path.exists(strFileName):
                self.dictMapAgentRecord = json.load(open(strFileName, 'r'))
                # with open(strFileName) as f:
                #     line = f.readline()
                #     self.dictMapAgentRecord = json.loads(line)
                #     print "restore index:{0}".format(line)
                #     print type(line)
                #     # self.dictCurrentIndex = json.loads(line)
                #     # print "load success file"
                #     f.close()
                if len(self.dictMapAgentRecord) > 0:
                    print "restore success"
                    print "content:{0}".format(json.dumps(self.dictMapAgentRecord))
                    # print "dict:{0}".format(self.dictMapAgentRecord)
            else:
                print "break point not exists: {0}".format(strFileName)
        except Exception as e:
            print "exception happend"
            print e.message
            print str(e)
            print 'str(Exception):\t', str(Exception)
            print 'str(e):\t\t', str(e)
            print 'repr(e):\t', repr(e)
            print 'e.message:\t', e.message
            print 'traceback.print_exc():'
            traceback.print_exc()
            print 'traceback.format_exc():\n%s' % (traceback.format_exc())

    def debug(self):
        print "debug info: dictMapAgentRecord:{0}".format(json.dumps(self.dictMapAgentRecord))


globalCommonPara = CommonPara()
globalCommonPara.initPara()
globalTaskManager = TaskManager()


def SaveEventToFile(msg='', code='', results=list(), actions=list(), level=''):
    print "enter SaveEventToFile"
    json_msg = {}
    if 1:
        try:
            json_msg = gen_report_msg("hd_map.pb", code, "/hd_map_agent")
        except Exception as e:
            print('Error: gen report msg failed!, {}'.format(e))
    print "++++++++++++++++++ event json_msg:{0}".format(json_msg)
    if json_msg == {}:  # if not used pb or call function error, used local config
        cur_time = int(time.time())
        msg_dict = {
            "timestamp": {
                "sec": cur_time,
                "nsec": int((time.time() - cur_time) * 1000000000)},
            "src": "/hd_map_agent",
            "code": code,
            "level": level,
            "result": results,
            "action": actions,
            "msg": msg
        }
        json_msg = json.dumps(msg_dict)
    try:
        with open("/home/mogo/data/log/msg_log/system_master_report.json", 'a+') as fp:
            # print("write mogo report event: {}".format(json_msg))
            fp.write(json_msg + '\n')
    except Exception as e:
        print('Error: save report msg to file, {}'.format(e))


g_CacheUtil = CacheUtils()


def checkFileMd5(strFileName):
    strFileMd5Value = ""
    if not os.path.exists(strFileName):
        return strFileMd5Value
    try:
        with open(strFileName, 'rb') as f:
            strFileMd5Value = str(hashlib.md5(f.read()).hexdigest())
            f.close()
        print "checkFileMd5: fileName:{0}, strFileMd5Value:{1}".format(strFileName, strFileMd5Value)
    except Exception as e:
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():'
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    return strFileMd5Value


def getFileCurStat(strFileName):
    ret = 0
    cur_offset = 0
    if not os.path.exists(strFileName):
        ret = -1
    try:
        with open(strFileName) as fp:
            fp.seek(0, os.SEEK_END)
            cur_offset = fp.tell()
            print "current_stat:{0}".format(cur_offset)
            fp.close()
    except Exception as e:
        print   "exception happend"
        print   e.message
        print   str(e)
        print   'str(Exception):\t', str(Exception)
        print   'str(e):\t\t', str(e)
        print   'repr(e):\t', repr(e)
        print   'e.message:\t', e.message
        print   'traceback.print_exc():'
        traceback.print_exc()
        print   'traceback.format_exc():\n%s' % (traceback.format_exc())
    return ret, int(cur_offset)


# def downFileFromUrl(strUrl, strTempFileName):
#     ret = 0
#     retFileStat = 0
#     intFromOffset = 0
#     retFileStat ,intFromOffset = getFileCurStat(strTempFileName)
#     data = None
#     intErrno = 0
#     # 20*1024*1024
#     down_speed = 5 * 1024 * 1024
#     try:
#         html = StringIO.StringIO()
#         c = pycurl.Curl()
#         if  os.path.exists(strTempFileName) and retFileStat == 0  and intFromOffset  > 0:
#             c.setopt(pycurl.CURLOPT_RESUME_FROM_LARGE,intFromOffset)
#         c.setopt(pycurl.WRITEFUNCTION, html.write)
#         c.setopt(pycurl.FOLLOWLOCATION, 1)
#         c.setopt(pycurl.MAXREDIRS, 5)
#         c.setopt(pycurl.CONNECTTIMEOUT, 60)
#         c.setopt(pycurl.TIMEOUT, 300)
#         f = open(strTempFileName, 'wb')
#         c.setopt(c.WRITEDATA, f)
#         c.setopt(pycurl.URL, strUrl)
#         c.setopt(pycurl.FOLLOWLOCATION, 1)
#         c.setopt(c.NOPROGRESS, 1)
#         c.setopt(c.MAX_RECV_SPEED_LARGE, down_speed * 8)
#         c.perform()
#         print "downFileFromUrl status:{0}".format(c.getinfo(pycurl.HTTP_CODE), c.getinfo(pycurl.EFFECTIVE_URL))
#
#     except Exception as e:
#         print "exception happend"
#         print e.message
#         print str(e)
#         print 'str(Exception):\t', str(Exception)
#         print 'str(e):\t\t', str(e)
#         print 'repr(e):\t', repr(e)
#         print 'e.message:\t', e.message
#         print 'traceback.print_exc():'
#         traceback.print_exc()
#         print 'traceback.format_exc():\n%s' % (traceback.format_exc())
#         ret = -1
#     return ret, strTempFileName


def downFileFromUrlWget(strUrl, strTempFileName):
    ret = 0
    down_speed = 5 * 1024 * 1024
    strWgetCmd = " /usr/bin/wget  --limit-rate=4m   --connect-timeout=5 --dns-timeout=5  -c    '{0}'  -O   '{1}' ".format(
        strUrl, strTempFileName)
    try:
        print   "execute sub cmd : {0}".format(strWgetCmd)
        status, output = commands.getstatusoutput(strWgetCmd)
        print   "status:{0}".format(status)
        ret = status
    except Exception as e:
        print "exception happend"
        print   e.message
        print   str(e)
        print   'str(Exception):\t', str(Exception)
        print   'str(e):\t\t', str(e)
        print   'repr(e):\t', repr(e)
        print   'e.message:\t', e.message
        print   'traceback.print_exc():'
        traceback.print_exc()
        print   'traceback.format_exc():\n%s' % (traceback.format_exc())
        ret = -1
    return ret, strTempFileName


def syncFromCloud(strUrl, strMd5, strTempFileName):
    retNum = 0
    try_times = 0
    try:
        while True:
            if globalPilotMode == 1:
                retNum = -1
                break
            try_times = try_times + 1
            if try_times > global_MaxTryTimes:
                print "Exit  Download  , Download file try times:{0} more than global_MaxTryTimes:{1}".format(try_times,
                                                                                                              global_MaxTryTimes)
                retNum = -1
                break

            if try_times <= global_MaxTryTimes:
                retDownload, strTempFileName = downFileFromUrlWget(strUrl, strTempFileName)
                ## download files success
                if retDownload == 0:
                    ## check md5 Success
                    if checkFileMd5(strTempFileName) == strMd5:
                        print "md5 check success:filename:{0}".format(strTempFileName)
                        retNum = 0
                        break
                    ##  check md5 failed
                    if checkFileMd5(strTempFileName) != strMd5:
                        print "md5 check failed:filename:{0}".format(strTempFileName)
                ## download file failed
                if retDownload != 0:
                    print "Download file failed,try times:{0}".format(try_times)
                # if os.path.exists(strTempFileName):
                #     os.remove(strTempFileName)

    except Exception as e:
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():'
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    return retNum


def link_file(strDownStageLocationFileMap, strStandardLocationFileMap):
    ret = 0
    try:
        if os.path.exists(strDownStageLocationFileMap):
            while True:
                if (os.path.exists(strStandardLocationFileMap)) and (
                        os.readlink(strStandardLocationFileMap) == strDownStageLocationFileMap):
                    print   "############ link file:{0}  and target_file:{1} name normal".format(
                        strStandardLocationFileMap, strDownStageLocationFileMap)
                    break
                if (os.path.exists(strStandardLocationFileMap)) and (
                        os.readlink(strStandardLocationFileMap) != strDownStageLocationFileMap):
                    print   "############ link file:{0}  and target_file:{1} name abnormal".format(
                        strStandardLocationFileMap, strDownStageLocationFileMap)
                    os.remove(strStandardLocationFileMap)
                    os.symlink(strDownStageLocationFileMap, strStandardLocationFileMap)
                    ret = 1
                    break
                if not os.path.exists(strStandardLocationFileMap):
                    print "link file: {0} not exists ,now create ".format(strStandardLocationFileMap)
                    os.symlink(strDownStageLocationFileMap, strStandardLocationFileMap)
                    ret = 1
                    break
                break
        else:
            print  "src file:{0} not exists, link failed".format(strDownStageLocationFileMap)
            ret = -1

    except Exception as e:
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():'
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    return ret


def processFile(lMapId, strMapUrl, strMapMd5, timestamp, strStandardLocationFileMap):
    print "--------------------------processFile: lMapId:{0}, strMapUrl:{1}, strMapMd5:{2}, timestamp:{3}".format(
        lMapId, strMapUrl, strMapMd5, timestamp)

    intProcessRet = 0

    if int(lMapId) < 0 or int(lMapId) == 0:
        print "processFile recv para error line_id"
        intProcessRet = 1

    if len(strMapUrl.strip()) == 0:
        print "processFile recv para error strMapUrl"
        intProcessRet = 1

    if len(strMapMd5.strip()) == 0:
        print "processFile recv para error strMapMd5"
        intProcessRet = 1

    global g_CacheUtil

    strHistoryDownTempLocationFileMap = ""
    strHistoryDownStageLocationFileMap = ""
    if intProcessRet == 0:
        intDownCompleteMapStatus = 0
        strDownTempLocationFileMap = "{0}/map_{1}_{2}".format(globalStrTempDownFolder, lMapId, timestamp)
        strDownStageLocationFileMap = "{0}/map_{1}_{2}".format(globalStrStageDownFolder, lMapId, timestamp)
        if g_CacheUtil.dictMapAgentRecord.has_key(lMapId):
            strHistoryDownTempLocationFileMap = "{0}/map_{1}_{2}".format(globalStrTempDownFolder, lMapId,
                                                                         g_CacheUtil.dictMapAgentRecord[lMapId][
                                                                             'timestamp'])
            strHistoryDownStageLocationFileMap = "{0}/map_{1}_{2}".format(globalStrStageDownFolder, lMapId,
                                                                          g_CacheUtil.dictMapAgentRecord[lMapId][
                                                                              'timestamp'])
        try:
            ## check temp Download folder exists
            if os.path.isdir(globalStrTempDownFolder) and os.access(globalStrTempDownFolder, os.R_OK):
                print "folder exists and is readable"
            else:
                print "folder not ready,now create path"
                os.makedirs(globalStrTempDownFolder)
                print os.path.isdir(globalStrTempDownFolder)
                os.chmod(globalStrTempDownFolder, 0777)

            if os.path.isdir(globalStrStageDownFolder) and os.access(globalStrStageDownFolder, os.R_OK):
                print
                "folder exists and is readable"
            else:
                print
                "folder not ready,now create path"
                os.makedirs(globalStrStageDownFolder)
                print os.path.isdir(globalStrStageDownFolder)
                os.chmod(globalStrStageDownFolder, 0777)

            print "strStandardLocationFileMap:{0}".format(strStandardLocationFileMap)
            listDirs = strStandardLocationFileMap.split('/')
            print "listDirs:{0}".format(listDirs)

            strStandardLocationFolder = ""
            if len(listDirs) > 3:
                sublist = listDirs[1:-1]
                print  "sublist:{0}".format(sublist)
                strStandardLocationFolder = "/" + "/".join(sublist)
                print  "strStandardLocationFolder:{0}".format(strStandardLocationFolder)

            if len(strStandardLocationFolder) > 1:
                if os.path.isdir(strStandardLocationFolder) and os.access(strStandardLocationFolder, os.R_OK):
                    print   "folder:{0} exists and is readable".format(strStandardLocationFolder)
                else:
                    print   "folder:{0} not ready,now create path".format(strStandardLocationFolder)
                    os.makedirs(strStandardLocationFolder)
                    print  os.path.isdir(strStandardLocationFolder)
                    os.chmod(strStandardLocationFolder, 0777)

            ### check Downfile
            while True:
                # if os.path.exists(strDownTempLocationFileMap):
                #     os.remove(strDownTempLocationFileMap)

                print "--------------------before switch not g_CacheUtil.CheckMapFileCacheExists"
                if not g_CacheUtil.CheckMapFileCacheExists(lMapId, timestamp, strMapMd5):
                    print "########## enter switch not g_CacheUtil.CheckMapFileCacheExists(lMapId, timestamp, strMapMd5)"
                    ## down to temp  location
                    intCheckStatus = 0
                    intCheckStatus = syncFromCloud(strMapUrl, strMapMd5, strDownTempLocationFileMap)
                    print "=============intCheckStatus:{0}".format(intCheckStatus)
                    if intCheckStatus == 0:
                        intDownCompleteMapStatus = 1
                    if intCheckStatus != 0:
                        intDownCompleteMapStatus = 2
                        if os.path.exists(strDownStageLocationFileMap) == True:
                            intDownCompleteMapStatus = 3

                print "--------------------------before switch (g_CacheUtil.CheckMapFileCacheExists(lMapId, timestamp, strMapMd5) == True) and (os.path.exists(strDownStageLocationFileMap)"
                print g_CacheUtil.debug()
                print "input map_id:{0}".format(lMapId)
                print "strDownStageLocationFileMap:{0}".format(strDownStageLocationFileMap)
                if (g_CacheUtil.CheckMapFileCacheExists(lMapId, timestamp, strMapMd5) == True) and (
                        os.path.exists(strHistoryDownStageLocationFileMap)):
                    print "===enter switch (g_CacheUtil.CheckMapFileCacheExists(lMapId, timestamp, strMapMd5) == True) and (os.path.exists(strHistoryDownStageLocationFileMap))"
                    intLocationTimeStamp = int(os.path.getmtime(strHistoryDownStageLocationFileMap))

                    strMapName = "{0}".format(lMapId)
                    intCacheModifyNameMap = g_CacheUtil.dictMapAgentRecord[strMapName]['modify_time']
                    print "## +++++++++++++++++++++++++++++intCacheModifyNameMap:{0},intLocationTimeStamp:{1}".format(
                        intCacheModifyNameMap, intLocationTimeStamp)
                    while True:
                        ## local cache  file same with  hd_map_file
                        if intLocationTimeStamp == intCacheModifyNameMap:
                            # compare timestamp
                            if g_CacheUtil.dictMapAgentRecord[strMapName]['timestamp'] == timestamp:
                                print "====== enter g_CacheUtil.dictMapAgentRecord[strMapName]['timestamp'] == timestamp"
                                ### direct use
                                intDownCompleteMapStatus = 4
                                break

                            if g_CacheUtil.dictMapAgentRecord[strMapName]['timestamp'] != timestamp:
                                print "======= enter g_CacheUtil.dictMapAgentRecord[strMapName]['timestamp'] != timestamp"
                                ##  download file
                                intCheckStatus = 0
                                intCheckStatus = syncFromCloud(strMapUrl, strMapMd5, strDownTempLocationFileMap)
                                if intCheckStatus == 0:
                                    intDownCompleteMapStatus = 1
                                if intCheckStatus != 0:
                                    intDownCompleteMapStatus = 2
                                    if os.path.exists(strDownStageLocationFileMap):
                                        intDownCompleteMapStatus = 3
                                break
                        ## local cache  file not same with  hd_map_file
                        if intLocationTimeStamp > intCacheModifyNameMap:
                            ## local  happend change , compare   new timestamp  and local modify_time
                            print "########## map intLocationTimeStamp > intCacheModifyNameMap"
                            if intLocationTimeStamp > timestamp:
                                print "===enter switch intLocationTimeStamp > timestamp====="
                                intDownCompleteMapStatus = 3
                            else:
                                print "===enter switch intLocationTimeStamp <=  timestamp====="
                                ###  use cloud hd_map
                                intCheckStatus = 0
                                intCheckStatus = syncFromCloud(strMapUrl, strMapMd5, strDownTempLocationFileMap)
                                if intCheckStatus == 0:
                                    intDownCompleteMapStatus = 1
                                if intCheckStatus != 0:
                                    intDownCompleteMapStatus = 2
                                    if os.path.exists(strDownStageLocationFileMap):
                                        intDownCompleteMapStatus = 3
                            break
                        ## local cache  file not same with  hd_map_file
                        # if intLocationTimeStamp < intCacheModifyNameMap:
                        #     print "########## map intLocationTimeStamp < intCacheModifyNameMap"
                        #     ##direct use
                        #     break
                        break
                    break
                print "strDownStageLocationFileMap:{0}".format(strDownStageLocationFileMap)
                if os.path.exists(strDownStageLocationFileMap):
                    print "====enter switch  os.path.exists(strDownStageLocationFileMap)"
                    # intDownCompleteStopStatus = 3
                    intDownCompleteMapStatus = 3
                    break
                break

            ## start replace  file
            print "-------------status intDownCompleteMapStatus:{0}".format(intDownCompleteMapStatus)
            while True:
                if intDownCompleteMapStatus == 1:
                    print "##########(intDownCompleteMapStatus  == 1)"
                    print "++++++++++=copy file str:{0},dst:{1}".format(strDownTempLocationFileMap,
                                                                        strDownStageLocationFileMap)

                    shutil.copyfile(strDownTempLocationFileMap, strDownStageLocationFileMap)
                    intLocationStampMap = int(os.path.getmtime(strDownStageLocationFileMap))

                    g_CacheUtil.WriteFileCacheInfo(lMapId, strMapUrl, strMapMd5, timestamp, intLocationStampMap)
                    # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_SUCCESS', results=list(), actions=list(), level='info')
                    print "=====DOWNLOAD_SUCCESS"
                    if link_file(strDownStageLocationFileMap, strStandardLocationFileMap) == 1:
                        print "============== happend relink , transter to pad"
                        SaveEventToFile(msg='', code='ISYS_CONFIG_UPDATE_HADMAP', results=list(), actions=list(),level='info')

                    intProcessRet = 0
                    break
                if intDownCompleteMapStatus == 2:
                    print "##########intDownCompleteMapStatus == False   or  intDownCompleteStopStatus == False happend"
                    # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_FAILURE', results=list(), actions=list(),level='info')
                    intProcessRet = 1
                    print  "=====DOWNLOAD_FAILURE"
                    break
                if intDownCompleteMapStatus == 3:
                    print "##########remote map not exists,now user local map"
                    # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_WARNING', results=list(), actions=list(),level='warn')
                    intProcessRet = 2
                    print "=====LOCAL_HD_MAP_FIRST_WARNING"
                    if link_file(strDownStageLocationFileMap, strStandardLocationFileMap) == 1:
                        print "============== happend relink , transter to pad"
                        SaveEventToFile(msg='', code='ISYS_CONFIG_UPDATE_HADMAP', results=list(), actions=list(),level='info')
                    break
                if intDownCompleteMapStatus == 4:
                    print "########## map same with cloud ,not need  update "
                    # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_SUCCESS', results=list(), actions=list(),level='info')
                    intProcessRet = 0
                    print "===== LOCAL_SAME_AS_CLOUD_NOT_NEED_UPDATE"
                    if link_file(strDownStageLocationFileMap, strStandardLocationFileMap) == 1:
                        print "============== happend relink , transter to pad"
                        SaveEventToFile(msg='', code='ISYS_CONFIG_UPDATE_HADMAP', results=list(), actions=list(),level='info')
                    break
                break



        except Exception as e:
            print "exception happend"
            print e.message
            print str(e)
            print 'str(Exception):\t', str(Exception)
            print 'str(e):\t\t', str(e)
            print 'repr(e):\t', repr(e)
            print 'e.message:\t', e.message
            print 'traceback.print_exc():'
            traceback.print_exc()
            print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    return intProcessRet


def ControlCmd(strJsonControlCmd):
    pass


def call_process(strReponse):
    print "-----------------------call_process recv task-----------------"
    global globalTaskManager
    try:
        dictResult = None
        dictResult = json.loads(strReponse)
        if dictResult is not None and len(dictResult) > 0:
            intErrorCode = int(dictResult['errcode'])
            strMsg = str(dictResult['msg'])
            intMapId = str(dictResult['data']['mapId'])
            intPid = str(dictResult['data']['pid'])
            strCosPath = str(dictResult['data']['cosPath'])
            # strPath = str(dictResult['data']['path'])
            strPath = "/home/mogo/autopilot/share/hadmap_engine/data/hadmap_data/db.sqlite.backup"
            strMd5 = str(dictResult['data']['md5'])
            strMapVersion = str(dictResult['data']['mapVersion'])
            strUpdateTime = str(dictResult['data']['updateTime'])

            strTime = "2022-06-30T06:14:52.000+00:00"
            listSubTime = strUpdateTime.split('+')

            print   "listSubTime:{0}".format(listSubTime)
            strSimpleTime = ""
            if len(listSubTime) == 2:
                if len(listSubTime[0]) > 0:
                    listSubSubTime = listSubTime[0].split('.000')
                    if len(listSubSubTime) == 2 and len(listSubSubTime[0]) > 0:
                        strSimpleTime = listSubSubTime[0]
            print   "-------------- strSimpleTime:{0}".format(strSimpleTime)
            timeArray = time.strptime(strSimpleTime, "%Y-%m-%dT%H:%M:%S")
            intTranslateUpdateTime = int(time.mktime(timeArray))
            print "call_process: recv  lMapId:{0}, strMapUrl:{1}, strMapMd5:{2},timestamp:{3},strVersion:{4}".format(
                intPid, strCosPath, strMd5, intTranslateUpdateTime, strMapVersion)
            # download map
            strTaskId = "{0}_{1}".format(intPid, intTranslateUpdateTime)
            while True:
                if 1:
                    # globalTaskManager.addTask(strTaskId)
                    # print "-----   task_id:{0} ".format(strTaskId)
                    intResultProcess = processFile(intPid, strCosPath, strMd5, intTranslateUpdateTime, strPath)
                    if intResultProcess == 0:
                        strIp = str("mdev-qa.zhidaohulian.com")
                        strPort = globalStrPort
                        strApiName = "/config/map/sync"
                        ## send  sync url
                        dictQueryCondition = {'vehicleConfSn': globalCommonPara.dictCarInfo['car_plate'],
                                              'mapId': intMapId,
                                              'pid': intPid}
                        print "=========== request sync info : {0}".format(dictQueryCondition)
                        strSyncResponse = simpleHttpsQuery(strIp, strPort, strApiName, dictQueryCondition)
                        print "=========== response sync info: {0}".format(strSyncResponse)
                        #SaveEventToFile(msg='', code='ISYS_CONFIG_UPDATE_HADMAP', results=list(), actions=list(),level='info')

                        if len(strSyncResponse) > 0:
                            dictResponse = json.loads(strSyncResponse)
                            intSyncResponseErrorCode = int(dictResponse['errcode'])
                            intSyncResponseMsg = str(dictResponse['msg'])
                            # print "strSyncResponse:{0}".format(strSyncResponse)
                    break
                break
    except Exception as e:
        print "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():'
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())
    finally:
        globalTaskManager.removeTask(strTaskId)


def topicMsgCallback(msg):
    global globalPilotMode
    # print "--------------------------------------------------recv from channel /chassis/vehicle_state  "
    pbStatus = common_vehicle_state_pb2.VehicleState()
    pbStatus.ParseFromString(msg.data)
    globalPilotMode = pbStatus.pilot_mode
    # print "=--------------/chassis/vehicle_state:recv  globalPilotMode:{0}".format(globalPilotMode)
    local_pid = os.getpid()
    if globalPilotMode == 1:
        # print "=========================globalPilotMode: {0}, start kill sub process".format(globalPilotMode)
        ## stop all sub wget task
        pids = psutil.pids()
        # print   "============pids:{0}".format(pids)
        for pid in pids:
            try:
                p = psutil.Process(pid)
                # print   "===================p:{0}".format(p)
                # print   "====================p.ppid:{0}".format(p.ppid())
                if p.ppid() == local_pid:
                    print   "============found sub process,now kill, process  name{0}, pid: {1}".format(p.name(), p.pid)
                    if len(globalTaskManager.dictTaskInfo) > 0:
                        p.kill()
                        ## clean all  task info
                        globalTaskManager.delAllTask()
            except Exception as e:
                print   "exception happend"
                print   e.message
                print   str(e)
                print   'str(Exception):\t', str(Exception)
                print   'str(e):\t\t', str(e)
                print   'repr(e):\t', repr(e)
                print   'e.message:\t', e.message
                print   'traceback.print_exc():'
                traceback.print_exc()
                print   'traceback.format_exc():\n%s' % (traceback.format_exc())


def localizationCallback(msg):
    global globalMapPosition_latitude
    global globalMapPosition_longitude
    location = common_localization.Localization()
    location.ParseFromString(msg.data)
    globalMapPosition_longitude = location.longitude
    globalMapPosition_latitude = location.latitude
    # print "=====================globalMapPosition_longitude:{0}, globalMapPosition_latitude:{1}".format(globalMapPosition_longitude,globalMapPosition_latitude)


def addLocalizationListener():
    rospy.Subscriber("/chassis/vehicle_state", BinaryData, topicMsgCallback)
    rospy.Subscriber('/localization/global', BinaryData, localizationCallback)


def simpleHttpQuery(strIp, strPort, strApiName, dictQueryCondition):
    strJsonResult = ""
    dictHeader = {}
    dictHeader['Content-Type'] = "application/json"
    try:
        url = "http://{0}{1}".format(strIp, strApiName)
        ret = requests.post(url, headers=dictHeader, data=json.dumps(dictQueryCondition), timeout=3)
        s = ret.content.decode('utf8')
        j = json.loads(s)
        strJsonResult = json.dumps(j, sort_keys=True, indent=4)
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
    return strJsonResult


def simpleHttpsQuery(strIp, strPort, strApiName, dictQueryCondition):
    strJsonResult = ""
    dictHeader = {}
    dictHeader['Content-Type'] = "application/json"
    try:
        url = "https://{0}{1}".format(strIp, strApiName)
        print "simpleHttpsQuery url:{0}".format(url)
        ret = requests.post(url, headers=dictHeader, data=json.dumps(dictQueryCondition), timeout=3, verify=False)
        s = ret.content.decode('utf8')
        print "simpleHttpsQuery s:{0}".format(s)
        j = json.loads(s)
        strJsonResult = json.dumps(j, sort_keys=True, indent=4)
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
    return strJsonResult


def managerDownload(strReponse):
    global globalTaskManager
    print "-----------------------managerDownload recv task-----------------"
    if len(strReponse) > 0:
        try:
            dictResult = None
            dictResult = json.loads(strReponse)
            if dictResult is not None and len(dictResult) > 0:
                intErrorCode = int(dictResult['errcode'])
                strMsg = str(dictResult['msg'])
                intMapId = str(dictResult['data']['mapId'])
                intPid = str(dictResult['data']['pid'])
                strCosPath = str(dictResult['data']['cosPath'])
                strPath = str(dictResult['data']['path'])
                strMd5 = str(dictResult['data']['md5'])
                strMapVersion = str(dictResult['data']['mapVersion'])
                strUpdateTime = str(dictResult['data']['updateTime'])

                strTime = "2022-06-30T06:14:52.000+00:00"
                listSubTime = strUpdateTime.split('+')
                print "listSubTime:{0}".format(listSubTime)
                strSimpleTime = ""
                if len(listSubTime) == 2:
                    if len(listSubTime[0]) > 0:
                        listSubSubTime = listSubTime[0].split('.000')
                        if len(listSubSubTime) == 2 and len(listSubSubTime[0]) > 0:
                            strSimpleTime = listSubSubTime[0]
                print "-------------- strSimpleTime:{0}".format(strSimpleTime)
                timeArray = time.strptime(strSimpleTime, "%Y-%m-%dT%H:%M:%S")
                intTranslateUpdateTime = int(time.mktime(timeArray))
                print "call_process: recv  lMapId:{0}, strMapUrl:{1}, strMapMd5:{2},timestamp:{3},strVersion:{4}".format(
                    intPid, strCosPath, strMd5, intTranslateUpdateTime, strMapVersion)
                # download map
                strTaskId = "{0}_{1}".format(intPid, intTranslateUpdateTime)
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

        if not globalTaskManager.checkTaskExists(strTaskId):
            ## autopilot status cannot down hd map
            if globalPilotMode == 0:
                globalTaskManager.addTask(strTaskId)
                globalDownloadWorkerRequestPool.submit(call_process, strReponse)


def doCheckMapInfo():
    strReponse = ""
    while True:
        strIp = "mdev-qa.zhidaohulian.com"
        strApiName = "/config/map/list"
        try:
            dictCarInfo = globalCommonPara.read_car_info()
            strCarSn = dictCarInfo['car_plate']
            dictQueryCondition = {'vehicleConfSn': strCarSn, 'lng': globalMapPosition_longitude,
                                  'lat': globalMapPosition_latitude}
            print  "========================== query map info:{0}".format(json.dumps(dictQueryCondition))
            strReponse = simpleHttpsQuery(strIp, globalStrPort, strApiName, dictQueryCondition)
            print  "========================== response map info:{0}".format(strReponse)
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
        if len(strReponse) > 0:
            globalManagerProcessRequestPool.submit(managerDownload, strReponse)
            # call_process(strReponse)
        time.sleep(60)


class TryUpdateHdMapThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        doCheckMapInfo()


def main():
    try:
        # initial node
        rospy.init_node('map_agent', anonymous=True)
        # add listener.lis
        addLocalizationListener()
        ## start thread
        sys_update_hd_map_thread = TryUpdateHdMapThread()
        sys_update_hd_map_thread.start()
        ## wait msg
        rospy.spin()
    except Exception as e:
        print  "exception happend"
        print e.message
        print str(e)
        print 'str(Exception):\t', str(Exception)
        print 'str(e):\t\t', str(e)
        print 'repr(e):\t', repr(e)
        print 'e.message:\t', e.message
        print 'traceback.print_exc():';
        traceback.print_exc()
        print 'traceback.format_exc():\n%s' % (traceback.format_exc())


if __name__ == "__main__":
    try:
        # prepare_env()
        main()
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
