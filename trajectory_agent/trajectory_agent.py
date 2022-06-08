#!/usr/bin/env python
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

from autopilot_msgs.msg import BinaryData
import proto.trajectory_agent_sync_status_pb2  as common_trajectory_agent_sync_status_pb2
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




tree = lambda: collections.defaultdict(tree)

global_MaxTryTimes = 5

globalProcessRequestPool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='ProcessRequestPool')

globalPubToSystemMasterStatus = rospy.Publisher("/trajectory_agent/cmd/status",BinaryData,queue_size=1000)

class CacheUtils:
    dictTrajectoryAgentRecord = None
    strDictSaveTime = None

    def __init__(self):
        self.dictTrajectoryAgentRecord = tree()
        self.strDictSaveTime="/home/mogo/data/trajectory_agent_cache_record.json"
        self.restoreIndex()

    def WriteFileCacheInfo(self, lLineId,strTrajUrl, strTrajMd5,strStopUrl, strStopMd5, timestamp):
        print "process WriteFileCacheInfo: lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2},strStopUrl:{3},strStopMd5:{4},timestamp:{5}".format(lLineId,strTrajUrl,strTrajMd5,strStopUrl,strStopMd5,timestamp)
        try:
            strTrajName = "traj_{0}.csv".format(lLineId)
            print "strTrajName:{0}".format(strTrajName)
            self.dictTrajectoryAgentRecord[strTrajName]['url'] = strTrajUrl
            self.dictTrajectoryAgentRecord[strTrajName]['timestamp'] = timestamp
            self.dictTrajectoryAgentRecord[strTrajName]['md5'] = strTrajMd5


            strStopName = "stop_{0}.txt".format(lLineId)
            print "strStopName:{0".format(strStopName)
            self.dictTrajectoryAgentRecord[strStopName]["url"] = strStopUrl
            self.dictTrajectoryAgentRecord[strStopName]["timestamp"] = timestamp
            self.dictTrajectoryAgentRecord[strStopName]['md5'] = strStopMd5

            print "=======================current dictTrajectoryAgentRecord:{0}".format(json.dumps(self.dictTrajectoryAgentRecord))

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
            if (self.dictStopRecord.has_key(strStopName)) and (self.dictStopRecord['timestamp'] == timestamp) and \
                    (self.dictStopRecord['md5'] == strStopMd5):
                bExists = True
            else:
                bExists = False
            print "CheckStopFileCacheExists check file:{0}, result:{1}".format(strStopName,bExists)
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
            if (self.dictTrajRecord.has_key(strTrajName)) and (self.dictTrajRecord['timestamp'] == timestamp) and \
                    (self.dictTrajRecord['md5'] == strTrajMd5):
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


g_CacheUtil = CacheUtils()


def checkFileMd5(strFileName):
    strFileMd5Value = ""
    try:
        with open(strFileName,'rb') as f:
            strFileMd5Value=str(hashlib.md5(f.read()))
            f.close()
        print "checkFileMd5: fileName:{0}, strFileMd5Value:{1}".format(strFileName,strFileMd5Value)
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
    strTempFileName = ""
    intErrno = 0
    strBase64Content = ""
    strOriginContent =  ""
    try:
        request = urllib2.Request(strUrl)
        response = urllib2.urlopen(request,timeout=60)
        content = response.read()
        dictContent = None
        if len(content) > 0:
            print json.loads(content)
            dictContent = json.loads(content)
            if dictContent.has_key('errno'):
                intErrno  = int(dictContent['errno'])
                print "strUrl:{0},intErrno:{1}".format(strUrl,intErrno)
            if  (intErrno == 0) and (dictContent.has_key('data')):
                strBase64Content = str(dictContent['result'])
        if len(strBase64Content) > 0:
            strOriginContent = base64.b64decode(strBase64Content).decode()
            with open(strTempFileName)  as f:
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
    print "processFile: lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3}, strStopMd5:{4}, timestamp:{5}".format(lLineId,strTrajUrl,strTrajMd5,strStopUrl,strStopMd5,timestamp)
    intProcessRet = 0
    global g_CacheUtil
    intDownCompleteStopStatus = 0
    intDownCompleteTrajStatus = 0
    strStandardLocationFileStop = "/home/mogo/data/stop_{0}.txt".format(lLineId)
    strStandardLocationFileTraj = "/home/mogo/data/traj_{0}.csv".format(lLineId)

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
        ### check Downfile
        while True:
            # clear temp down load file
            if os.path.exists(strDownTempLocationFileStop):
                os.remove(strDownTempLocationFileStop)
            if os.path.exists(strDownTempLocationFileTraj):
                os.remove(strDownTempLocationFileTraj)

            if not g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5):
                ## down to temp  location
                intCheckStatus = 0
                intCheckStatus = syncFromCloud(strTrajUrl, strTrajMd5, strDownTempLocationFileTraj)
                if intCheckStatus == 0:
                    intDownCompleteTrajStatus  = 1
                if intCheckStatus  !=  0 :
                    intDownCompleteTrajStatus  = 2


            if not g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5):
                ## down to temp  location
                intCheckStatus = 0
                intCheckStatus = syncFromCloud(strStopUrl, strStopMd5, strDownTempLocationFileStop)
                if  intCheckStatus == 0:
                    intDownCompleteStopStatus = 1
                if intCheckStatus  != 0 :
                    intDownCompleteStopStatus = 2
                break

            if (g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5) == True) and (
                    os.path.exists(strStandardLocationFileTraj)):
                intLocationTimeStamp = int(os.path.getmtime(strStandardLocationFileTraj))
                while True:
                    if intLocationTimeStamp == timestamp:
                        # compare md5
                        if checkFileMd5(strStandardLocationFileTraj) == strTrajMd5:
                            ### direct use
                            break

                        if checkFileMd5(strStandardLocationFileTraj) != strTrajMd5:
                            ##  download file
                            intCheckStatus = 0
                            intCheckStatus =  syncFromCloud(strTrajUrl, strTrajMd5, strDownTempLocationFileTraj)
                            if intCheckStatus == 0:
                                intDownCompleteTrajStatus = 1
                            if intCheckStatus != 0:
                                intDownCompleteTrajStatus = 2
                            break
                    if intLocationTimeStamp > timestamp:
                        ## direct use
                        break
                    if intLocationTimeStamp < timestamp:
                        ##direct use
                        break
                    break

            if (g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5) == True) and (
                    os.path.exists(strStandardLocationFileStop)):
                intLocationTimeStamp = int(os.path.getmtime(strStandardLocationFileTraj))
                while True:
                    if intLocationTimeStamp == timestamp:
                        # compare md5
                        if checkFileMd5(strStandardLocationFileStop) == strStopMd5:
                            ### direct use
                            break

                        if checkFileMd5(strStandardLocationFileStop) != strStopMd5:
                            ##  download file
                            intCheckStatus = 0
                            intCheckStatus = syncFromCloud(strStopUrl, strStopMd5, strDownTempLocationFileStop)
                            if intCheckStatus == 0:
                                intDownCompleteStopStatus =  1
                            if intCheckStatus != 0:
                                intDownCompleteStopStatus =  2
                            break
                    if intLocationTimeStamp > timestamp:
                        ## direct use
                        break
                    if intLocationTimeStamp < timestamp:
                        break
                    break
            break


        ## start replace  file
        while True:
            if (intDownCompleteTrajStatus  == 1)  and  (intDownCompleteStopStatus == 1) :
                print "(intDownCompleteTrajStatus  == 1)  and  (intDownCompleteStopStatus == 1)"
                #replace StandardPathFile
                shutil.copyfile(strDownTempLocationFileStop,strStandardLocationFileStop)
                shutil.copyfile(strDownTempLocationFileTraj,strStandardLocationFileTraj)
                g_CacheUtil.WriteFileCacheInfo(lLineId,strTrajUrl, strTrajMd5,strStopUrl, strStopMd5, timestamp)
                intProcessRet = 0
                break
            if (intDownCompleteTrajStatus == 2)   or  (intDownCompleteStopStatus == 2):
                print "intDownCompleteTrajStatus == False   or  intDownCompleteStopStatus == False happend"
                intProcessRet = 1
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
        pbLine=common_message_pad_pb2.Line()
        pbLine.ParseFromString(msg.data)
        #parse pb msg
        lLineId=pbLine.lineId
        strTrajUrl=pbLine.trajUrl
        strTrajMd5 =pbLine.trajMd5
        strStopUrl = pbLine.stopUrl
        strStopMd5  = pbLine.stopMd5
        timestamp = pbLine.timestamp
        strVersion = pbLine.vehicleModel
        print "call_process: recv  lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3},strStopMd5:{4},timestamp:{5},strVersion:{6}".format(lLineId,strTrajUrl,strTrajMd5,strStopUrl,strStopMd5,timestamp,strVersion)
        #call process File
        intResultProcess = processFile(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp)

        pbSend = common_trajectory_agent_sync_status_pb2.TrajectoryAgentSyncStatus()
        pbSend.header.seq = 1
        pbSend.header.stamp.sec = rostime.Time.now().secs
        pbSend.header.stamp.nsec = rostime.Time.now().nsecs
        pbSend.header.frame_id = "trajectory_agent_frame_id"
        pbSend.header.module_name = "trajectory_agent"

        if intResultProcess  == 0:
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
        globalProcessRequestPool.submit(call_process,msg)

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