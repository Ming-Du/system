#!/usr/bin/env python
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import base64
import collections
import json
import traceback
import os
import shutil
import hashlib
import urllib2

import thread
import threading
import traceback
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
import proto.trajectory_agent_sync_status_pb2 as common_trajectory_agent_sync_status_pb2
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
path.append(os.path.dirname(__file__)+'/../mogo_reporter/script/')
#sys.path.append('../mogo_reporter/script/')
from get_msg_by_code import gen_report_msg

tree = lambda: collections.defaultdict(tree)

global_MaxTryTimes = 6

globalProcessRequestPool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='ProcessRequestPool')

globalPubToSystemMasterStatus = rospy.Publisher("/trajectory_agent/cmd/status", BinaryData, queue_size=1000)


class CacheUtils:
    dictTrajectoryAgentRecord = None
    strDictSaveTime = None

    def __init__(self):
        self.dictTrajectoryAgentRecord = tree()
        self.strDictSaveTime = "/home/mogo/data/trajectory_agent_cache_record.json"
        self.restoreIndex()

    def WriteFileCacheInfo(self, lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestampTraj,timestampStop,intModifyTime_Traj,intModifyTime_Stop):
        print "process WriteFileCacheInfo: lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2},strStopUrl:{3},strStopMd5:{4},timestampTraj:{5},timestampStop:{6},intModifyTime_Traj:{7},intModifyTime_Stop:{8}".format(
            lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestampTraj,timestampStop,intModifyTime_Traj,intModifyTime_Stop)
        try:
            strTrajName = "traj_{0}.csv".format(lLineId)
            print "strTrajName:{0}".format(strTrajName)
            self.dictTrajectoryAgentRecord[strTrajName]['url'] = strTrajUrl
            self.dictTrajectoryAgentRecord[strTrajName]['timestamp'] = timestampTraj
            self.dictTrajectoryAgentRecord[strTrajName]['md5'] = strTrajMd5
            self.dictTrajectoryAgentRecord[strTrajName]['modify_time'] = intModifyTime_Traj

            strStopName = "stop_{0}.txt".format(lLineId)
            print "strStopName:{0}".format(strStopName)
            self.dictTrajectoryAgentRecord[strStopName]["url"] = strStopUrl
            self.dictTrajectoryAgentRecord[strStopName]["timestamp"] = timestampStop
            self.dictTrajectoryAgentRecord[strStopName]['md5'] = strStopMd5
            self.dictTrajectoryAgentRecord[strStopName]['modify_time']=intModifyTime_Stop

            print "=======================current dictTrajectoryAgentRecord:{0}".format(
                json.dumps(self.dictTrajectoryAgentRecord))

            with open(self.strDictSaveTime, 'w') as f:
                json.dump(self.dictTrajectoryAgentRecord, f)
                print "flush file"
                f.close()


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

    def CheckStopFileCacheExists(self, lLineId, timestamp, strStopMd5):
        bExists = True
        try:
            strStopName = "stop_{0}.txt".format(lLineId)
            if (self.dictTrajectoryAgentRecord.has_key(strStopName)) and (
                    self.dictTrajectoryAgentRecord[strStopName]['timestamp'] == timestamp) and \
                    (self.dictTrajectoryAgentRecord[strStopName]['md5'] == strStopMd5):
                bExists = True
            else:
                bExists = False
            print "CheckStopFileCacheExists check file:{0}, result:{1}".format(strStopName, bExists)
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

    def CheckTrajFileCacheExists(self, lLineId, timestamp, strTrajMd5):
        bExists = True
        try:
            strTrajName = "traj_{0}.csv".format(lLineId)
            if (self.dictTrajectoryAgentRecord.has_key(strTrajName)) and (
                    self.dictTrajectoryAgentRecord[strTrajName]['timestamp'] == timestamp) and \
                    (self.dictTrajectoryAgentRecord[strTrajName]['md5'] == strTrajMd5):
                bExists = True
            else:
                bExists = False
            print "CheckTrajFileCacheExists check file:{0}, result:{1}".format(strTrajName, bExists)
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
                with open(strFileName) as f:
                    line = f.readline()
                    self.dictTrajectoryAgentRecord = json.loads(line)
                    print "restore index:{0}".format(line)
                    print type(line)
                    # self.dictCurrentIndex = json.loads(line)
                    # print "load success file"
                    f.close()
                    if len(self.dictTrajectoryAgentRecord) > 0:
                        print "restore success"
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
    # def checkFileCacheChangeStatus(self, strLocationFile, lLineId, timestamp, strStopMd5):
    #     intFlag = 0
    #     try:
    #         while True:
    #             if not os.path.exists(strLocationFile):
    #                 intFlag = -1
    #                 break
    #             if os.path.exists(strLocationFile) and self.CheckStopFileCacheExists(lLineId, timestamp,
    #                                                                                      strStopMd5):
    #                 intLocationTimeStamp = int(os.path.getmtime(strLocationFile))
    #                 if intLocationTimeStamp == timestamp:
    #                     intFlag = 0
    #                     break
    #                 if intLocationTimeStamp != timestamp:
    #                     intFlag = 1
    #                     break
    #             break
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


def SaveEventToFile(msg='', code='', results=list(), actions=list(), level=''):
    print "enter SaveEventToFile"
    json_msg = {}
    if 1:
        try:
            json_msg = gen_report_msg("trajectory_agent.pb", code, "/trajectory_agent")
        except Exception as e:
            print('Error: gen report msg failed!, {}'.format(e))
    print "++++++++++++++++++ event json_msg:{0}".format(json_msg)
    if json_msg == {}:  # if not used pb or call function error, used local config
        cur_time = int(time.time())
        msg_dict = {
            "timestamp": {
                "sec": cur_time,
                "nsec": int((time.time() - cur_time) * 1000000000)},
            "src": "/trajectory_agent",
            "code": code,
            "level": level,
            "result": results,
            "action": actions,
            "msg": msg
        }
        json_msg = json.dumps(msg_dict)
    try:
        with open("/home/mogo/data/log/msg_log/trajectory_agent.json",'a+') as fp:
            print("write mogo report event: {}".format(msg))
            fp.write(json_msg + '\n')
    except Exception as e:
        print('Error: save report msg to file, {}'.format(e))




g_CacheUtil = CacheUtils()


def checkFileMd5(strFileName):
    strFileMd5Value = ""
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


def downFileFromUrl(strUrl, strTempFileName):
    ret = 0
    data = None
    # strTempFileName = ""
    intErrno = 0
    strBase64Content = ""
    strOriginContent = ""
    try:
        request = urllib2.Request(strUrl)
        response = urllib2.urlopen(request, timeout=60)
        content = response.read()
        dictContent = None
        if len(content) > 0:
            # print json.loads(content)
            dictContent = json.loads(content)
            if dictContent.has_key('errno'):
                intErrno = int(dictContent['errno'])
                print "====================================================================================strUrl:{0},intErrno:{1}".format(
                    strUrl, intErrno)
            if (intErrno == 0) and (dictContent.has_key('result')):
                print "-------------------enter  (intErrno == 0) and (dictContent.has_key('result')) and  strTempFileName:{0} ".format(
                    strTempFileName)
                strBase64Content = str(dictContent['result'])
        if len(strBase64Content) > 0:
            strOriginContent = base64.b64decode(strBase64Content).decode()
            # print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  strOriginContent:{0}".format(strOriginContent)
            print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ strTempFileName:{0}".format(strTempFileName)
            # os._exit(-1)
            if os.path.exists(strTempFileName):
                os.remove(strTempFileName)
            with open(strTempFileName, 'ab+') as f:
                f.write(strOriginContent)
                f.close()
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
    return ret, strTempFileName


def syncFromCloud(strUrl, strMd5, strTempFileName):
    retNum = 0
    try_times = 0
    try:
        while True:
            try_times = try_times + 1
            if try_times > global_MaxTryTimes:
                print "Exit  Download  , Download file try times:{0} more than global_MaxTryTimes:{1}".format(try_times,
                                                                                                              global_MaxTryTimes)
                retNum = -1
                break

            if try_times <= global_MaxTryTimes:
                retDownload, strTempFileName = downFileFromUrl(strUrl, strTempFileName)
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


def processFile(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp):
    print "--------------------------processFile: lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3}, strStopMd5:{4}, timestamp:{5}".format(
        lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp)

    intProcessRet = 0
    global g_CacheUtil
    intDownCompleteStopStatus = 0
    intDownCompleteTrajStatus = 0
    strStandardLocationFileStop = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/JL/stop_{0}.txt".format(
        lLineId)
    strStandardLocationFileTraj = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/JL/traj_{0}.csv".format(
        lLineId)

    strDownTempLocationFileStop = "/home/mogo/data/down_traj_agent_tmp/stop_{0}.txt".format(lLineId)
    strDownTempLocationFileTraj = "/home/mogo/data/down_traj_agent_tmp/traj_{0}.csv".format(lLineId)
    try:
        ## check temp Download folder exists
        strTempDownFolder = '/home/mogo/data/down_traj_agent_tmp/'
        if os.path.isdir(strTempDownFolder) and os.access(strTempDownFolder, os.R_OK):
            print "folder exists and is readable"
        else:
            print "folder not ready,now create path"
            os.makedirs(strTempDownFolder)
            print os.path.isdir(strTempDownFolder)
            os.chmod(strTempDownFolder, 0777)

        strTempDownFolder = '/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/JL/'
        if os.path.isdir(strTempDownFolder) and os.access(strTempDownFolder, os.R_OK):
            print
            "folder exists and is readable"
        else:
            print
            "folder not ready,now create path"
            os.makedirs(strTempDownFolder)
            print
            os.path.isdir(strTempDownFolder)
            os.chmod(strTempDownFolder, 0777)

        ### check Downfile
        while True:
            # clear temp down load file
            if os.path.exists(strDownTempLocationFileStop):
                os.remove(strDownTempLocationFileStop)
            if os.path.exists(strDownTempLocationFileTraj):
                os.remove(strDownTempLocationFileTraj)

            if not g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5):
                print "##########not g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5)"
                ## down to temp  location
                intCheckStatus = 0
                intCheckStatus = syncFromCloud(strTrajUrl, strTrajMd5, strDownTempLocationFileTraj)
                if intCheckStatus == 0:
                    intDownCompleteTrajStatus = 1
                if intCheckStatus != 0:
                    intDownCompleteTrajStatus = 2
                    if os.path.exists(strStandardLocationFileTraj) == True:
                        intDownCompleteTrajStatus = 3


            # os._exit(-1)

            if not g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5):
                print "##########not g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5)"
                ## down to temp  location
                intCheckStatus = 0
                intCheckStatus = syncFromCloud(strStopUrl, strStopMd5, strDownTempLocationFileStop)
                if intCheckStatus == 0:
                    intDownCompleteStopStatus = 1
                if intCheckStatus != 0:
                    intDownCompleteStopStatus = 2
                    if os.path.exists(strStandardLocationFileStop) == True:
                        intDownCompleteStopStatus = 3
                print "strDownTempLocationFileStop:{0}".format(strDownTempLocationFileStop)
                break
            # os.__exit(-1)

            if (g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5) == True) and (
                    os.path.exists(strStandardLocationFileTraj)):
                intLocationTimeStamp = int(os.path.getmtime(strStandardLocationFileTraj))

                strTrajName="traj_{0}.csv".format(lLineId)
                intCacheModifyNameTraj = g_CacheUtil.dictTrajectoryAgentRecord[strTrajName]['modify_time']
                print "+++++++++++++++++++++++++++++intCacheModifyNameTraj:{0},intLocationTimeStamp:{1}".format(intCacheModifyNameTraj,intLocationTimeStamp)
                while True:
                    if intLocationTimeStamp == intCacheModifyNameTraj:
                        # compare md5
                        if checkFileMd5(strStandardLocationFileTraj) == strTrajMd5:
                            print "##########intLocationTimeStamp == intCacheModifyNameTraj ,  checkFileMd5(strStandardLocationFileTraj) == " \
                                  "strTrajMd5 "
                            ### direct use
                            break

                        if checkFileMd5(strStandardLocationFileTraj) != strTrajMd5:
                            print "##########intLocationTimeStamp == intCacheModifyNameTraj, checkFileMd5(strStandardLocationFileTraj) != " \
                                  "strTrajMd5 "
                            ##  download file
                            intCheckStatus = 0
                            intCheckStatus = syncFromCloud(strTrajUrl, strTrajMd5, strDownTempLocationFileTraj)
                            if intCheckStatus == 0:
                                intDownCompleteTrajStatus = 1
                            if intCheckStatus != 0:
                                intDownCompleteTrajStatus = 2
                            break
                    if intLocationTimeStamp > intCacheModifyNameTraj:
                        print "########## traj intLocationTimeStamp > intCacheModifyNameTraj"
                        ## direct use
                        break
                    if intLocationTimeStamp < intCacheModifyNameTraj:
                        print "########## traj intLocationTimeStamp < intCacheModifyNameTraj"
                        ##direct use
                        break
                    break
            if (g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5) == True) and (
                    os.path.exists(strStandardLocationFileStop)):
                intLocationTimeStamp = int(os.path.getmtime(strStandardLocationFileTraj))
                strStopName = "traj_{0}.csv".format(lLineId)
                intCacheModifyNameStop = g_CacheUtil.dictTrajectoryAgentRecord[strStopName]['modify_time']
                print "++++++++++++++++++++++++++++++intCacheModifyNameStop:{0},intLocationTimeStamp:{1}".format(intCacheModifyNameStop,intLocationTimeStamp)
                while True:
                    if intLocationTimeStamp == intCacheModifyNameStop:
                        # compare md5
                        if checkFileMd5(strStandardLocationFileStop) == strStopMd5:
                            print "##########intLocationTimeStamp == intCacheModifyNameStop , checkFileMd5(strStandardLocationFileStop) == strStopMd5"
                            ### direct use
                            break

                        if checkFileMd5(strStandardLocationFileStop) != strStopMd5:
                            print "##########intLocationTimeStamp == intCacheModifyNameStop, checkFileMd5(strStandardLocationFileStop) != strStopMd5"
                            ##  download file
                            intCheckStatus = 0
                            intCheckStatus = syncFromCloud(strStopUrl, strStopMd5, strDownTempLocationFileStop)
                            if intCheckStatus == 0:
                                intDownCompleteStopStatus = 1
                            if intCheckStatus != 0:
                                intDownCompleteStopStatus = 2
                            break
                    if intLocationTimeStamp > intCacheModifyNameStop:
                        print "########## stop intLocationTimeStamp > intCacheModifyNameStop"
                        ## direct use
                        break
                    if intLocationTimeStamp < intCacheModifyNameStop:
                        print "########## stop intLocationTimeStamp < intCacheModifyNameStop"
                        break
                    break
                break
            if os.path.exists(strStandardLocationFileStop) and os.path.exists(strStandardLocationFileTraj):
                intDownCompleteStopStatus = 3
                intDownCompleteTrajStatus = 3
                break
            break

        ## start replace  file
        while True:
            if (intDownCompleteTrajStatus == 1) and (intDownCompleteStopStatus == 1):
                print "##########(intDownCompleteTrajStatus  == 1)  and  (intDownCompleteStopStatus == 1)"
                # replace StandardPathFile
                print "++++++++++=copy file str:{0},dst:{1}".format(strDownTempLocationFileStop,strStandardLocationFileStop)
                print "++++++++++=copy file str:{0},dst:{1}".format(strDownTempLocationFileTraj,strStandardLocationFileTraj)
                shutil.copyfile(strDownTempLocationFileStop, strStandardLocationFileStop)
                shutil.copyfile(strDownTempLocationFileTraj, strStandardLocationFileTraj)
                intLocationStampTraj = int(os.path.getmtime(strStandardLocationFileTraj))
                intLocationStampStop = int(os.path.getmtime(strStandardLocationFileStop))
                g_CacheUtil.WriteFileCacheInfo(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5,timestamp,timestamp,intLocationStampTraj,intLocationStampStop)
                print "============================================================================================="
                SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_SUCCESS', results=list(), actions=list(), level='info')
                intProcessRet = 0
                break
            if (intDownCompleteTrajStatus == 2) or (intDownCompleteStopStatus == 2):
                print "##########intDownCompleteTrajStatus == False   or  intDownCompleteStopStatus == False happend"
                print "============================================================================================="
                SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_FAILURE', results=list(), actions=list(),level='info')
                intProcessRet = 1
                break
            if (intDownCompleteTrajStatus == 3) and (intDownCompleteStopStatus == 3):
                print "##########remote traj not exists,now user local traj"
                print "============================================================================================="
                SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_WARNING', results=list(), actions=list(),level='info')
                intProcessRet = 0
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


def call_process(msg):
    try:
        pbLine = common_message_pad_pb2.TrajectoryDownloadReq()
        pbLine.ParseFromString(msg.data)
        # parse pb msg
        lLineId = pbLine.line.lineId
        strTrajUrl = pbLine.line.trajUrl
        print "type:{0}".format(type(pbLine.line.trajMd5))
        strTempTrajMd5 = str(pbLine.line.trajMd5)
        strTrajMd5 = strTempTrajMd5
        print "!!!!!!!!!!!!!!!!!!!!!strTrajMd5:{0}".format(strTrajMd5)
        strStopUrl = pbLine.line.stopUrl
        strTempStopMd5 = str(pbLine.line.stopMd5)
        strStopMd5 = strTempStopMd5
        print "!!!!!!!!!!!!!!!!!!!!strStopMd5:{0}".format(strStopMd5)
        timestamp = pbLine.line.timestamp
        strVersion = pbLine.line.vehicleModel
        print "call_process: recv  lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3},strStopMd5:{4},timestamp:{5},strVersion:{6}".format(
            lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, strVersion)
        # call process File
        intResultProcess = processFile(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp)

        pbSend = common_trajectory_agent_sync_status_pb2.TrajectoryAgentSyncStatus()
        pbSend.header.seq = 1
        pbSend.header.stamp.sec = rospy.Time.now().secs
        pbSend.header.stamp.nsec = rospy.Time.now().nsecs
        pbSend.header.frame_id = "trajectory_agent_frame_id"
        pbSend.header.module_name = "trajectory_agent"

        if intResultProcess == 0:
            pbSend.sync_status = 0
            print "pbSend.sync_status = 0"
        else:
            pbSend.sync_status = -1
            print "pbSend.sync_status = -1"

        strBuffer = pbSend.SerializeToString()
        rosMessage = BinaryData()
        rosMessage.data = strBuffer
        rosMessage.size = len(strBuffer)
        globalPubToSystemMasterStatus.publish(rosMessage)

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


def topicMsgCallback(msg):
    print "--------------------------------------------------recv from channel /trajectory_agent/cmd/transaction "
    if msg.size > 0:
        globalProcessRequestPool.submit(call_process, msg)


def addLocalizationListener():
    strRecvTopic = "/trajectory_agent/cmd/transaction"
    strSendTopic = "/trajectory_agent/cmd/status"
    rospy.Subscriber("/trajectory_agent/cmd/transaction", BinaryData, topicMsgCallback)


def main():
    # initial node
    rospy.init_node('trajectory_agent', anonymous=True)
    # add listener
    addLocalizationListener()
    ## wait msg
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("monitor.py is failed !")
        exit(0)
