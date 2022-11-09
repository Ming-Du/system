#!/usr/bin/env python
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d]' '- %(levelname)s: %(message)s',
                    level=logging.INFO)
logging.debug('debug message')
import os
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor
import proto.message_pad_pb2 as common_message_pad_pb2

import rospy

from InterfaceDataSource import InterfaceDataSource
from Job import Job
from JobItem import JobItem
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool

from CacheUtils import CacheUtils
from CommonUtilsReadFile import CommonUtilsReadFile
from CommonPara import CommonPara
from CommonHttpUtils import CommonHttpUtils
from CommonSchedulerImpInterfaceTaskSchedulingPool import CommonSchedulerImpInterfaceTaskSchedulingPool
from EnumDataSourceType import EnumDataSourceType
from CommonUtilsCompare import CommonUtilsCompare
from EnumJobType import EnumJobType

import std_msgs
from std_msgs.msg import String
from rospy import init_node, Subscriber
import json
from autopilot_msgs.msg import BinaryData
from EnumJobType import EnumJobType

instanceCommonUtils = CommonUtilsCompare()
instanceReadConfigFile = CommonUtilsReadFile()
instanceScheduler = CommonSchedulerImpInterfaceTaskSchedulingPool()
instanceCacheUtils = CacheUtils("/home/mogo/data/trajectory_agent_cache_record.json")

globalProcessRequestPool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ProcessRequestPool')
globalPubToSystemMasterStatus = rospy.Publisher("/trajectory_agent/cmd/status", BinaryData, queue_size=1000)


def processFileV250(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, floatStartX, floatStartY,
                    floatEndX, floatEndY):
    rospy.loginfo(
        "--------------v250------------processFile: lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3}, strStopMd5:{4}, timestamp:{5},floatStartX:{6}, floatStartY:{7}, floatEndX{8}, floatEndY:{9}".format(
            lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, floatStartX, floatStartY, floatEndX,
            floatEndY))
    intCheckInputPara = 0

    intProcessRet = -1
    intDownCompleteStopStatus = 0
    intDownCompleteTrajStatus = 0
    strStandardLocationFileStop = ""
    strStandardLocationFileTraj = ""
    strDownTempLocationFileStop = ""
    strDownTempLocationFileTraj = ""
    global g_CacheUtil

    if int(lLineId) > 0:
        intDownCompleteStopStatus = 0
        intDownCompleteTrajStatus = 0
        strStandardLocationFileStop = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/DF/stop_{0}.txt".format(
            lLineId)
        strStandardLocationFileTraj = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/DF/traj_{0}.csv".format(
            lLineId)
        strDownTempLocationFileStop = "/home/mogo/data/down_traj_agent_tmp/stop_{0}.txt".format(lLineId)
        strDownTempLocationFileTraj = "/home/mogo/data/down_traj_agent_tmp/traj_{0}.csv".format(lLineId)
        if int(timestamp) == 0 or len(strTrajUrl.strip()) == 0 or len(strTrajMd5.strip()) == 0 or len(
                strStopUrl.strip()) == 0 or len(strStopMd5.strip()) == 0:
            if os.path.exists(strStandardLocationFileTraj) and os.path.exists(strStandardLocationFileStop):
                intDownCompleteStopStatus = 3
                intDownCompleteTrajStatus = 3

        if int(timestamp) > 0 and len(strTrajUrl.strip()) > 0 and len(strTrajMd5.strip()) > 0 and len(
                strStopUrl.strip()) > 0 and len(strStopMd5.strip()) > 0:

            try:
                ## check temp Download folder exists
                strTempDownFolder = '/home/mogo/data/down_traj_agent_tmp/'
                if os.path.isdir(strTempDownFolder) and os.access(strTempDownFolder, os.R_OK):
                    pass
                else:
                    rospy.logwarn("folder not ready,now create path")
                    os.makedirs(strTempDownFolder)
                    os.chmod(strTempDownFolder, 0777)

                strTempDownFolder = '/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/DF/'
                if os.path.isdir(strTempDownFolder) and os.access(strTempDownFolder, os.R_OK):
                    pass
                else:
                    rospy.logwarn("folder not ready,now create path")
                    os.makedirs(strTempDownFolder)
                    os.chmod(strTempDownFolder, 0777)

                ### check Downfile
                while True:
                    # clear temp down load file
                    if os.path.exists(strDownTempLocationFileStop):
                        os.remove(strDownTempLocationFileStop)
                    if os.path.exists(strDownTempLocationFileTraj):
                        os.remove(strDownTempLocationFileTraj)
                    strStopTemp = strDownTempLocationFileStop + ".temp"
                    strTrajTemp = strDownTempLocationFileTraj + ".temp"
                    if os.path.exists(strStopTemp):
                        os.remove(strStopTemp)
                    if os.path.exists(strTrajTemp):
                        os.remove(strTrajTemp)

                    rospy.logdebug("before switch not g_CacheUtil.CheckTrajFileCacheExists")
                    ## clear Incomplete complete line info
                    if (os.path.exists(strStandardLocationFileTraj) == False) or (
                            os.path.exists(strStandardLocationFileStop) == False):
                        if os.path.exists(strStandardLocationFileTraj):
                            os.remove(strStandardLocationFileTraj)
                        if os.path.exists(strStandardLocationFileStop):
                            os.remove(strStandardLocationFileStop)
                    if os.path.exists(strStandardLocationFileTraj) == False:
                        rospy.logdebug(
                            "########## enter switch not g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5)")
                        ## down to temp  location
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break
                        intCheckStatus = 0
                        intCheckStatus = syncFromCloud(strTrajUrl, strTrajMd5, strDownTempLocationFileTraj, lLineId)
                        rospy.logdebug("=============intCheckStatus:{0}".format(intCheckStatus))
                        if intCheckStatus == 0:
                            intDownCompleteTrajStatus = 1
                        if intCheckStatus != 0:
                            intDownCompleteTrajStatus = 2
                            if os.path.exists(strStandardLocationFileTraj) == True:
                                intDownCompleteTrajStatus = 3

                    # os._exit(-1)
                    rospy.logdebug("------------------------before switch g_CacheUtil.CheckStopFileCacheExists")
                    if os.path.exists(strStandardLocationFileStop) == False:
                        rospy.logdebug(
                            "########## enter switch not g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5)")
                        ## down to temp  location
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break
                        intCheckStatus = 0
                        intCheckStatus = syncFromCloud(strStopUrl, strStopMd5, strDownTempLocationFileStop, lLineId)
                        rospy.logdebug("=============intCheckStatus:{0}".format(intCheckStatus))
                        if intCheckStatus == 0:
                            intDownCompleteStopStatus = 1
                        if intCheckStatus != 0:
                            intDownCompleteStopStatus = 2
                            if os.path.exists(strStandardLocationFileStop) == True:
                                intDownCompleteStopStatus = 3
                        rospy.logdebug("strDownTempLocationFileStop:{0}".format(strDownTempLocationFileStop))
                        break
                    # os.__exit(-1)
                    rospy.logdebug(
                        "--------------------------before switch (g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5) == True) and (os.path.exists(strStandardLocatio)")
                    if (g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5) == True) and (
                            os.path.exists(strStandardLocationFileTraj)):
                        rospy.logdebug(
                            "===enter switch (g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5) == True) and (os.path.exists(strStandardLocationFileTraj))")
                        intLocationTimeStamp = int(os.path.getmtime(strStandardLocationFileTraj))
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break

                        strTrajName = "traj_{0}.csv".format(lLineId)
                        intCacheModifyNameTraj = g_CacheUtil.dictTrajectoryAgentRecord[strTrajName]['modify_time']
                        rospy.logdebug(
                            "+++++++++++++++++++++++++++++intCacheModifyNameTraj:{0},intLocationTimeStamp:{1}".format(
                                intCacheModifyNameTraj, intLocationTimeStamp))
                        while True:
                            if intLocationTimeStamp == intCacheModifyNameTraj:
                                # compare md5
                                # if checkFileMd5(strStandardLocationFileTraj) == strTrajMd5:
                                if g_CacheUtil.dictTrajectoryAgentRecord[strTrajName]['md5'] == strTrajMd5:
                                    rospy.logdebug(
                                        "##########intLocationTimeStamp == intCacheModifyNameTraj ,  checkFileMd5(strStandardLocationFileTraj) == " \
                                        "strTrajMd5 ")
                                    ### direct use
                                    intDownCompleteTrajStatus = 4
                                    break

                                # if checkFileMd5(strStandardLocationFileTraj) != strTrajMd5:
                                if g_CacheUtil.dictTrajectoryAgentRecord[strTrajName]['md5'] != strTrajMd5:
                                    rospy.logdebug(
                                        "##########intLocationTimeStamp == intCacheModifyNameTraj, checkFileMd5(strStandardLocationFileTraj) != " \
                                        "strTrajMd5 ")
                                    ##  download file
                                    intCheckStatus = 0
                                    intCheckStatus = syncFromCloud(strTrajUrl, strTrajMd5, strDownTempLocationFileTraj,
                                                                   lLineId)
                                    if intCheckStatus == 0:
                                        intDownCompleteTrajStatus = 1
                                    if intCheckStatus != 0:
                                        intDownCompleteTrajStatus = 2
                                        if os.path.exists(strStandardLocationFileTraj):
                                            intDownCompleteTrajStatus = 3
                                    break
                            if intLocationTimeStamp > intCacheModifyNameTraj:
                                rospy.logdebug("########## traj intLocationTimeStamp > intCacheModifyNameTraj")
                                ## direct use
                                intDownCompleteTrajStatus = 3
                                break
                            if intLocationTimeStamp < intCacheModifyNameTraj:
                                rospy.logdebug("########## traj intLocationTimeStamp < intCacheModifyNameTraj")
                                ##direct use
                                intDownCompleteTrajStatus = 3
                                break
                            break
                    rospy.logdebug(
                        "----------------------------------before switch (g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5) == True) and (os.path.exists(strStandardLocationFileStop))")
                    if (g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5) == True) and (
                            os.path.exists(strStandardLocationFileStop)):
                        rospy.logdebug(
                            "enter switch (g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5) == True) and (os.path.exists(strStandardLocationFileStop))")
                        intLocationTimeStamp = int(os.path.getmtime(strStandardLocationFileStop))
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break
                        strStopName = "stop_{0}.txt".format(lLineId)
                        intCacheModifyNameStop = g_CacheUtil.dictTrajectoryAgentRecord[strStopName]['modify_time']
                        rospy.logdebug(
                            "++++++++++++++++++++++++++++++intCacheModifyNameStop:{0},intLocationTimeStamp:{1}".format(
                                intCacheModifyNameStop, intLocationTimeStamp))
                        while True:
                            if intLocationTimeStamp == intCacheModifyNameStop:
                                # compare md5
                                # if checkFileMd5(strStandardLocationFileStop) == strStopMd5:
                                if g_CacheUtil.dictTrajectoryAgentRecord[strStopName]['md5'] == strStopMd5:
                                    rospy.logdebug(
                                        "##########intLocationTimeStamp == intCacheModifyNameStop , checkFileMd5(strStandardLocationFileStop) == strStopMd5")
                                    ### direct use
                                    intDownCompleteStopStatus = 4
                                    break

                                # if checkFileMd5(strStandardLocationFileStop) != strStopMd5:
                                if g_CacheUtil.dictTrajectoryAgentRecord[strStopName]['md5'] != strStopMd5:
                                    rospy.logdebug(
                                        "##########intLocationTimeStamp == intCacheModifyNameStop, checkFileMd5(strStandardLocationFileStop) != strStopMd5")
                                    ##  download file
                                    intCheckStatus = 0
                                    intCheckStatus = syncFromCloud(strStopUrl, strStopMd5, strDownTempLocationFileStop,
                                                                   lLineId)
                                    if intCheckStatus == 0:
                                        intDownCompleteStopStatus = 1
                                    if intCheckStatus != 0:
                                        intDownCompleteStopStatus = 2
                                        if os.path.exists(strStandardLocationFileStop):
                                            intDownCompleteStopStatus = 3
                                    break
                            if intLocationTimeStamp > intCacheModifyNameStop:
                                rospy.logdebug("########## stop intLocationTimeStamp > intCacheModifyNameStop")
                                ## direct use
                                intDownCompleteStopStatus = 3
                                break
                            if intLocationTimeStamp < intCacheModifyNameStop:
                                rospy.logdebug("########## stop intLocationTimeStamp < intCacheModifyNameStop")
                                intDownCompleteStopStatus = 3
                                break
                            break
                        break
                    rospy.logdebug(
                        "---------------------------------------before switch os.path.exists(strStandardLocationFileStop) and os.path.exists(strStandardLocationFileTraj)")
                    rospy.logdebug("strStandardLocationFileStop:{0}".format(strStandardLocationFileStop))
                    rospy.logdebug("strStandardLocationFileTraj:{0}".format(strStandardLocationFileTraj))
                    if os.path.exists(strStandardLocationFileStop) and os.path.exists(strStandardLocationFileTraj):
                        rospy.logdebug(
                            "====enter switch  os.path.exists(strStandardLocationFileStop) and os.path.exists(strStandardLocationFileTraj)")
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break
                        intDownCompleteStopStatus = 3
                        intDownCompleteTrajStatus = 3
                        break
                    break
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    if (intDownCompleteStopStatus == 0 and intDownCompleteTrajStatus == 0) or (
            intDownCompleteStopStatus == 2 and intDownCompleteTrajStatus == 2):
        if float(floatStartX) > float(0.0) and float(floatStartY) > float(0.0) and float(floatEndX) > float(
                0.0) and float(floatEndY) > float(0.0):
            if CheckFileExistsByXAndY(floatStartX, floatStartY, floatEndX, floatEndY) == 0:
                intDownCompleteStopStatus = 5
                intDownCompleteTrajStatus = 5
            else:
                intDownCompleteStopStatus = 6
                intDownCompleteTrajStatus = 6

    ## start replace  file
    rospy.loginfo("-------------status intDownCompleteTrajStatus:{0},intDownCompleteStopStatus:{1}".format(
        intDownCompleteTrajStatus, intDownCompleteStopStatus))
    while True:
        if (intDownCompleteTrajStatus == 1) and (intDownCompleteStopStatus == 1):
            rospy.loginfo("##########(intDownCompleteTrajStatus  == 1)  and  (intDownCompleteStopStatus == 1)")
            # replace StandardPathFile
            # print "++++++++++=copy file str:{0},dst:{1}".format(strDownTempLocationFileStop,
            #                                                     strStandardLocationFileStop)
            # print "++++++++++=copy file str:{0},dst:{1}".format(strDownTempLocationFileTraj,
            #                                                     strStandardLocationFileTraj)
            shutil.copyfile(strDownTempLocationFileStop, strStandardLocationFileStop)
            if os.path.exists(strDownTempLocationFileStop):
                os.remove(strDownTempLocationFileStop)
            shutil.copyfile(strDownTempLocationFileTraj, strStandardLocationFileTraj)
            if os.path.exists(strDownTempLocationFileTraj):
                os.remove(strDownTempLocationFileTraj)
            intLocationStampTraj = int(os.path.getmtime(strStandardLocationFileTraj))
            intLocationStampStop = int(os.path.getmtime(strStandardLocationFileStop))
            g_CacheUtil.WriteFileCacheInfo(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp,
                                           timestamp, intLocationStampTraj, intLocationStampStop)
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_SUCCESS', results=list(), actions=list(), level='info')
            rospy.loginfo("===== V250 ISYS_INIT_TRAJECTORY_SUCCESS")
            intProcessRet = 0
            break
        if (intDownCompleteTrajStatus == 2) or (intDownCompleteStopStatus == 2):
            rospy.logdebug(
                "##########intDownCompleteTrajStatus == False   or  intDownCompleteStopStatus == False happend")
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_FAILURE', results=list(), actions=list(),level='info')
            intProcessRet = 1
            rospy.loginfo("===== V250 ISYS_INIT_TRAJECTORY_FAILURE")
            break
        if (intDownCompleteTrajStatus == 3) and (intDownCompleteStopStatus == 3):
            rospy.logdebug("##########remote traj not exists,now user local traj")
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_WARNING', results=list(), actions=list(),level='warn')
            intProcessRet = 2
            rospy.loginfo("===== V250 ISYS_INIT_TRAJECTORY_WARNING")
            break
        if (intDownCompleteTrajStatus == 4) and (intDownCompleteStopStatus == 4):
            rospy.logdebug("########## traj same with cloud ,not need  update ")
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_SUCCESS', results=list(), actions=list(),level='info')
            intProcessRet = 0
            rospy.loginfo("===== V250 ISYS_INIT_TRAJECTORY_SUCCESS")
            break
        if (intDownCompleteTrajStatus == 5) and (intDownCompleteStopStatus == 5):
            rospy.logdebug("########## V250  traj XY found V250 ")
            # print "============================================================================================="
            intProcessRet = 6
            rospy.loginfo("============ V250 intProcessRet = 6 ")
            break
        if (intDownCompleteTrajStatus == 6) and (intDownCompleteStopStatus == 6):
            rospy.logdebug("########## V250  traj XY not found  V250")
            # print "============================================================================================="
            intProcessRet = 8
            rospy.loginfo("============ V250 intProcessRet = 8 ")
            break
        if (os.path.exists(strStandardLocationFileStop) and os.path.exists(
                strStandardLocationFileTraj) and intDownCompleteTrajStatus == 1) or (
                os.path.exists(strStandardLocationFileStop) and os.path.exists(
            strStandardLocationFileTraj) and intDownCompleteStopStatus == 1):
            # replace StandardPathFile
            if os.path.exists(strDownTempLocationFileStop):
                shutil.copyfile(strDownTempLocationFileStop, strStandardLocationFileStop)
                os.remove(strDownTempLocationFileStop)
            if os.path.exists(strDownTempLocationFileTraj):
                shutil.copyfile(strDownTempLocationFileTraj, strStandardLocationFileTraj)
                os.remove(strDownTempLocationFileTraj)
            intLocationStampTraj = int(os.path.getmtime(strStandardLocationFileTraj))
            intLocationStampStop = int(os.path.getmtime(strStandardLocationFileStop))
            g_CacheUtil.WriteFileCacheInfo(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp,
                                           timestamp, intLocationStampTraj, intLocationStampStop)
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_SUCCESS', results=list(), actions=list(), level='info')
            rospy.loginfo("===== V250 ISYS_INIT_TRAJECTORY_SUCCESS_PART")
            intProcessRet = 0
            break
        break
    return intProcessRet


def processFileV260(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, floatStartX, floatStartY,
                    floatEndX, floatEndY):
    rospy.loginfo(
        "--------------v260------------processFile: lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3}, strStopMd5:{4}, timestamp:{5},floatStartX:{6}, floatStartY:{7}, floatEndX{8}, floatEndY:{9}".format(
            lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, floatStartX, floatStartY, floatEndX,
            floatEndY))
    intCheckInputPara = 0

    intProcessRet = -1
    intDownCompleteStopStatus = 0
    intDownCompleteTrajStatus = 0
    strStandardLocationFileStop = ""
    strStandardLocationFileTraj = ""
    strDownTempLocationFileStop = ""
    strDownTempLocationFileTraj = ""
    global g_CacheUtil

    if int(lLineId) > 0:
        intDownCompleteStopStatus = 0
        intDownCompleteTrajStatus = 0
        strStandardLocationFileStop = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/DF/stop_{0}.txt".format(
            lLineId)
        strStandardLocationFileTraj = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/DF/traj_{0}.csv".format(
            lLineId)
        strDownTempLocationFileStop = "/home/mogo/data/down_traj_agent_tmp_dpqp/stop_{0}.txt".format(lLineId)
        strDownTempLocationFileTraj = "/home/mogo/data/down_traj_agent_tmp_dpqp/traj_{0}.csv".format(lLineId)
        if int(timestamp) == 0 or len(strTrajUrl.strip()) == 0 or len(strTrajMd5.strip()) == 0 or len(
                strStopUrl.strip()) == 0 or len(strStopMd5.strip()) == 0:
            if os.path.exists(strStandardLocationFileTraj) and os.path.exists(strStandardLocationFileStop):
                intDownCompleteStopStatus = 3
                intDownCompleteTrajStatus = 3

        if int(timestamp) > 0 and len(strTrajUrl.strip()) > 0 and len(strTrajMd5.strip()) > 0 and len(
                strStopUrl.strip()) > 0 and len(strStopMd5.strip()) > 0:

            try:
                ## check temp Download folder exists
                strTempDownFolder = '/home/mogo/data/down_traj_agent_tmp_dpqp/'
                if os.path.isdir(strTempDownFolder) and os.access(strTempDownFolder, os.R_OK):
                    pass
                else:
                    rospy.loginfo("folder not ready,now create path")
                    os.makedirs(strTempDownFolder)

                    os.chmod(strTempDownFolder, 0777)

                strTempDownFolder = '/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/DF/'
                if os.path.isdir(strTempDownFolder) and os.access(strTempDownFolder, os.R_OK):
                    pass
                else:
                    rospy.loginfo("folder not ready,now create path")
                    os.makedirs(strTempDownFolder)
                    os.chmod(strTempDownFolder, 0777)

                ### check Downfile
                while True:
                    # clear temp down load file
                    if os.path.exists(strDownTempLocationFileStop):
                        os.remove(strDownTempLocationFileStop)
                    if os.path.exists(strDownTempLocationFileTraj):
                        os.remove(strDownTempLocationFileTraj)
                    strStopTemp = strDownTempLocationFileStop + ".temp"
                    strTrajTemp = strDownTempLocationFileTraj + ".temp"
                    if os.path.exists(strStopTemp):
                        os.remove(strStopTemp)
                    if os.path.exists(strTrajTemp):
                        os.remove(strTrajTemp)

                    rospy.logdebug("--------------------before switch not g_CacheUtil.CheckTrajFileCacheExists")
                    ## clear Incomplete complete line info
                    if (os.path.exists(strStandardLocationFileTraj) == False) or (
                            os.path.exists(strStandardLocationFileStop) == False):
                        if os.path.exists(strStandardLocationFileTraj):
                            os.remove(strStandardLocationFileTraj)
                        if os.path.exists(strStandardLocationFileStop):
                            os.remove(strStandardLocationFileStop)
                    if os.path.exists(strStandardLocationFileTraj) == False:
                        rospy.logdebug(
                            "########## enter switch not g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5)")
                        ## down to temp  location
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break
                        intCheckStatus = 0
                        intCheckStatus = syncFromCloud(strTrajUrl, strTrajMd5, strDownTempLocationFileTraj, lLineId)
                        rospy.logdebug("=============intCheckStatus:{0}".format(intCheckStatus))
                        if intCheckStatus == 0:
                            intDownCompleteTrajStatus = 1
                        if intCheckStatus != 0:
                            intDownCompleteTrajStatus = 2
                            if os.path.exists(strStandardLocationFileTraj) == True:
                                intDownCompleteTrajStatus = 3

                    # os._exit(-1)
                    rospy.logdebug("------------------------before switch g_CacheUtil.CheckStopFileCacheExists")
                    if os.path.exists(strStandardLocationFileStop) == False:
                        rospy.logdebug(
                            "########## enter switch not g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5)")
                        ## down to temp  location
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break
                        intCheckStatus = 0
                        intCheckStatus = syncFromCloud(strStopUrl, strStopMd5, strDownTempLocationFileStop, lLineId)
                        rospy.logdebug("=============intCheckStatus:{0}".format(intCheckStatus))
                        if intCheckStatus == 0:
                            intDownCompleteStopStatus = 1
                        if intCheckStatus != 0:
                            intDownCompleteStopStatus = 2
                            if os.path.exists(strStandardLocationFileStop) == True:
                                intDownCompleteStopStatus = 3
                        rospy.logdebug("strDownTempLocationFileStop:{0}".format(strDownTempLocationFileStop))
                        break
                    # os.__exit(-1)
                    rospy.logdebug(
                        "--------------------------before switch (g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5) == True) and (os.path.exists(strStandardLocatio)")
                    if (g_CacheUtil.CheckTrajFileCacheExistsDpqp(lLineId, timestamp, strTrajMd5) == True) and (
                            os.path.exists(strStandardLocationFileTraj)):
                        rospy.logdebug(
                            "===enter switch (g_CacheUtil.CheckTrajFileCacheExists(lLineId, timestamp, strTrajMd5) == True) and (os.path.exists(strStandardLocationFileTraj))")
                        intLocationTimeStamp = int(os.path.getmtime(strStandardLocationFileTraj))
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break

                        strTrajName = "traj_{0}.csv".format(lLineId)
                        intCacheModifyNameTraj = g_CacheUtil.dictTrajectoryAgentRecordDpqp[strTrajName]['modify_time']
                        rospy.logdebug(
                            "+++++++++++++++++++++++++++++intCacheModifyNameTraj:{0},intLocationTimeStamp:{1}".format(
                                intCacheModifyNameTraj, intLocationTimeStamp))
                        while True:
                            if intLocationTimeStamp == intCacheModifyNameTraj:
                                # compare md5
                                # if checkFileMd5(strStandardLocationFileTraj) == strTrajMd5:
                                if g_CacheUtil.dictTrajectoryAgentRecordDpqp[strTrajName]['md5'] == strTrajMd5:
                                    rospy.logdebug(
                                        "##########intLocationTimeStamp == intCacheModifyNameTraj ,  checkFileMd5(strStandardLocationFileTraj) == " \
                                        "strTrajMd5 ")
                                    ### direct use
                                    intDownCompleteTrajStatus = 4
                                    break

                                # if checkFileMd5(strStandardLocationFileTraj) != strTrajMd5:
                                if g_CacheUtil.dictTrajectoryAgentRecordDpqp[strTrajName]['md5'] != strTrajMd5:
                                    rospy.logdebug(
                                        "##########intLocationTimeStamp == intCacheModifyNameTraj, checkFileMd5(strStandardLocationFileTraj) != " \
                                        "strTrajMd5 ")
                                    ##  download file
                                    intCheckStatus = 0
                                    intCheckStatus = syncFromCloud(strTrajUrl, strTrajMd5, strDownTempLocationFileTraj,
                                                                   lLineId)
                                    if intCheckStatus == 0:
                                        intDownCompleteTrajStatus = 1
                                    if intCheckStatus != 0:
                                        intDownCompleteTrajStatus = 2
                                        if os.path.exists(strStandardLocationFileTraj):
                                            intDownCompleteTrajStatus = 3
                                    break
                            if intLocationTimeStamp > intCacheModifyNameTraj:
                                rospy.logdebug("########## traj intLocationTimeStamp > intCacheModifyNameTraj")
                                ## direct use
                                intDownCompleteTrajStatus = 3
                                break
                            if intLocationTimeStamp < intCacheModifyNameTraj:
                                rospy.logdebug("########## traj intLocationTimeStamp < intCacheModifyNameTraj")
                                ##direct use
                                intDownCompleteTrajStatus = 3
                                break
                            break
                    rospy.logdebug(
                        "----------------------------------before switch (g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5) == True) and (os.path.exists(strStandardLocationFileStop))")
                    if (g_CacheUtil.CheckStopFileCacheExistsDpqp(lLineId, timestamp, strStopMd5) == True) and (
                            os.path.exists(strStandardLocationFileStop)):
                        rospy.logdebug(
                            "enter switch (g_CacheUtil.CheckStopFileCacheExists(lLineId, timestamp, strStopMd5) == True) and (os.path.exists(strStandardLocationFileStop))")
                        intLocationTimeStamp = int(os.path.getmtime(strStandardLocationFileStop))
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break
                        strStopName = "stop_{0}.txt".format(lLineId)
                        intCacheModifyNameStop = g_CacheUtil.dictTrajectoryAgentRecordDpqp[strStopName]['modify_time']
                        rospy.logdebug(
                            "++++++++++++++++++++++++++++++intCacheModifyNameStop:{0},intLocationTimeStamp:{1}".format(
                                intCacheModifyNameStop, intLocationTimeStamp))
                        while True:
                            if intLocationTimeStamp == intCacheModifyNameStop:
                                # compare md5
                                # if checkFileMd5(strStandardLocationFileStop) == strStopMd5:
                                if g_CacheUtil.dictTrajectoryAgentRecordDpqp[strStopName]['md5'] == strStopMd5:
                                    rospy.logdebug(
                                        "##########intLocationTimeStamp == intCacheModifyNameStop , checkFileMd5(strStandardLocationFileStop) == strStopMd5")
                                    ### direct use
                                    intDownCompleteStopStatus = 4
                                    break

                                # if checkFileMd5(strStandardLocationFileStop) != strStopMd5:
                                if g_CacheUtil.dictTrajectoryAgentRecordDpqp[strStopName]['md5'] != strStopMd5:
                                    rospy.logdebug(
                                        "##########intLocationTimeStamp == intCacheModifyNameStop, checkFileMd5(strStandardLocationFileStop) != strStopMd5")
                                    ##  download file
                                    intCheckStatus = 0
                                    intCheckStatus = syncFromCloud(strStopUrl, strStopMd5, strDownTempLocationFileStop,
                                                                   lLineId)
                                    if intCheckStatus == 0:
                                        intDownCompleteStopStatus = 1
                                    if intCheckStatus != 0:
                                        intDownCompleteStopStatus = 2
                                        if os.path.exists(strStandardLocationFileStop):
                                            intDownCompleteStopStatus = 3
                                    break
                            if intLocationTimeStamp > intCacheModifyNameStop:
                                rospy.logdebug("########## stop intLocationTimeStamp > intCacheModifyNameStop")
                                intDownCompleteStopStatus = 3
                                ## direct use
                                break
                            if intLocationTimeStamp < intCacheModifyNameStop:
                                rospy.logdebug("########## stop intLocationTimeStamp < intCacheModifyNameStop")
                                intDownCompleteStopStatus = 3
                                break
                            break
                        break
                    rospy.logdebug(
                        "---------------------------------------before switch os.path.exists(strStandardLocationFileStop) and os.path.exists(strStandardLocationFileTraj)")
                    rospy.logdebug("strStandardLocationFileStop:{0}".format(strStandardLocationFileStop))
                    rospy.logdebug("strStandardLocationFileTraj:{0}".format(strStandardLocationFileTraj))
                    if os.path.exists(strStandardLocationFileStop) and os.path.exists(strStandardLocationFileTraj):
                        rospy.logdebug(
                            "====enter switch  os.path.exists(strStandardLocationFileStop) and os.path.exists(strStandardLocationFileTraj)")
                        # if globalDictTaskRunningStatus != lLineId:
                        #     break
                        intDownCompleteStopStatus = 3
                        intDownCompleteTrajStatus = 3
                        break
                    break
            except Exception as e:
                rospy.logwarn('repr(e):{0}'.format(repr(e)))
                rospy.logwarn('e.message:{0}'.format(e.message))
                rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    if (intDownCompleteStopStatus == 0 and intDownCompleteTrajStatus == 0) or (
            intDownCompleteStopStatus == 2 and intDownCompleteTrajStatus == 2):
        if float(floatStartX) > float(0.0) and float(floatStartY) > float(0.0) and float(floatEndX) > float(
                0.0) and float(floatEndY) > float(0.0):
            if CheckFileExistsByXAndYDpqp(floatStartX, floatStartY, floatEndX, floatEndY) == 0:
                intDownCompleteStopStatus = 5
                intDownCompleteTrajStatus = 5
            else:
                intDownCompleteStopStatus = 6
                intDownCompleteTrajStatus = 6

    ## start replace  file
    rospy.logdebug("-------------status intDownCompleteTrajStatus:{0},intDownCompleteStopStatus:{1}".format(
        intDownCompleteTrajStatus, intDownCompleteStopStatus))
    while True:
        if (intDownCompleteTrajStatus == 1) and (intDownCompleteStopStatus == 1):
            rospy.logdebug("##########(intDownCompleteTrajStatus  == 1)  and  (intDownCompleteStopStatus == 1)")
            # replace StandardPathFile
            rospy.logdebug("++++++++++=copy file str:{0},dst:{1}".format(strDownTempLocationFileStop,
                                                                         strStandardLocationFileStop))
            rospy.logdebug("++++++++++=copy file str:{0},dst:{1}".format(strDownTempLocationFileTraj,
                                                                         strStandardLocationFileTraj))
            shutil.copyfile(strDownTempLocationFileStop, strStandardLocationFileStop)
            if os.path.exists(strDownTempLocationFileStop):
                os.remove(strDownTempLocationFileStop)
            shutil.copyfile(strDownTempLocationFileTraj, strStandardLocationFileTraj)
            if os.path.exists(strDownTempLocationFileTraj):
                os.remove(strDownTempLocationFileTraj)
            intLocationStampTraj = int(os.path.getmtime(strStandardLocationFileTraj))
            intLocationStampStop = int(os.path.getmtime(strStandardLocationFileStop))
            g_CacheUtil.WriteFileCacheInfoDpqp(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp,
                                               timestamp, intLocationStampTraj, intLocationStampStop)
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_SUCCESS', results=list(), actions=list(), level='info')
            rospy.loginfo("===== V260 ISYS_INIT_TRAJECTORY_SUCCESS")
            intProcessRet = 3
            break
        if (intDownCompleteTrajStatus == 2) or (intDownCompleteStopStatus == 2):
            rospy.logdebug(
                "##########intDownCompleteTrajStatus == False   or  intDownCompleteStopStatus == False happend")
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_FAILURE', results=list(), actions=list(),level='info')
            intProcessRet = 4
            rospy.loginfo("===== V260 ISYS_INIT_TRAJECTORY_FAILURE")
            break
        if (intDownCompleteTrajStatus == 3) and (intDownCompleteStopStatus == 3):
            rospy.logdebug("##########remote traj not exists,now user local traj")
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_WARNING', results=list(), actions=list(),level='warn')
            intProcessRet = 5
            rospy.loginfo("===== V260 ISYS_INIT_TRAJECTORY_WARNING")
            break
        if (intDownCompleteTrajStatus == 4) and (intDownCompleteStopStatus == 4):
            rospy.logdebug("########## traj same with cloud ,not need  update ")
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_SUCCESS', results=list(), actions=list(),level='info')
            intProcessRet = 3
            rospy.loginfo("===== V260 ISYS_INIT_TRAJECTORY_SUCCESS")
            break
        if (intDownCompleteTrajStatus == 5) and (intDownCompleteStopStatus == 5):
            rospy.logdebug("########## V260  traj XY found V250 ")
            # print "============================================================================================="
            intProcessRet = 7
            rospy.loginfo("============ V250 intProcessRet = 6 ")
            break
        if (intDownCompleteTrajStatus == 6) and (intDownCompleteStopStatus == 6):
            rospy.logdebug("########## V260  traj XY not found  V250")
            # print "============================================================================================="
            intProcessRet = 9
            rospy.loginfo("============ V260 intProcessRet = 8 ")
            break
        if (os.path.exists(strStandardLocationFileStop) and os.path.exists(
                strStandardLocationFileTraj) and intDownCompleteTrajStatus == 1) or (
                os.path.exists(strStandardLocationFileStop) and os.path.exists(
            strStandardLocationFileTraj) and intDownCompleteStopStatus == 1):
            # replace StandardPathFile
            if os.path.exists(strDownTempLocationFileStop):
                shutil.copyfile(strDownTempLocationFileStop, strStandardLocationFileStop)
                os.remove(strDownTempLocationFileStop)
            if os.path.exists(strDownTempLocationFileTraj):
                shutil.copyfile(strDownTempLocationFileTraj, strStandardLocationFileTraj)
                os.remove(strDownTempLocationFileTraj)
            intLocationStampTraj = int(os.path.getmtime(strStandardLocationFileTraj))
            intLocationStampStop = int(os.path.getmtime(strStandardLocationFileStop))
            g_CacheUtil.WriteFileCacheInfoDpqp(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp,
                                               timestamp, intLocationStampTraj, intLocationStampStop)
            # print "============================================================================================="
            # SaveEventToFile(msg='', code='ISYS_INIT_TRAJECTORY_SUCCESS', results=list(), actions=list(), level='info')
            rospy.loginfo("===== V260 ISYS_INIT_TRAJECTORY_SUCCESS_PART")
            intProcessRet = 3
            break
        break
    return intProcessRet


def subFloat(floatValue):
    strFloat = "{0}".format(floatValue)
    listStr = strFloat.split(".")
    strNewPart2 = ""
    strFullValue = ""
    if len(listStr) == 2:
        if len(listStr[1]) > 5:
            strPart2 = listStr[1]
            strNewPart2 = strPart2[0:5]
        if len(listStr[1]) == 5:
            strNewPart2 = listStr[1]
        if len(listStr[1]) < 5 and len(listStr[1]) > 0:
            strNewPart2 = listStr[1]
            while True:
                strNewPart2 = strNewPart2 + '0'
                curLen = len(strNewPart2)
                if curLen == 5:
                    break
        strFullValue = "{0}.{1}".format(listStr[0], strNewPart2)
    return strFullValue


def CheckFileExistsByXAndYDpqp(floatStartX, floatStartY, floatEndX, floatEndY):
    strFileName1 = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/DF/traj_{0}_{1}_{2}_{3}_dpqp.csv".format(
        subFloat(floatStartX), subFloat(floatStartY), subFloat(floatEndX), subFloat(floatEndY))
    strFileName2 = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data_dpqp/DF/stop_{0}_{1}_{2}_{3}_dpqp.txt".format(
        subFloat(floatStartX), subFloat(floatStartY), subFloat(floatEndX), subFloat(floatEndY))
    ret = 0
    rospy.logdebug("strFileName1:{0}".format(strFileName1))
    rospy.logdebug("strFileName2:{0}".format(strFileName2))
    if os.path.exists(strFileName1) and os.path.exists(strFileName2):
        ret = 0
    else:
        ret = -1
    return ret


def CheckFileExistsByXAndY(floatStartX, floatStartY, floatEndX, floatEndY):
    strFileName1 = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/DF/traj_{0}_{1}_{2}_{3}.csv".format(
        subFloat(floatStartX), subFloat(floatStartY), subFloat(floatEndX), subFloat(floatEndY))
    strFileName2 = "/home/mogo/data/vehicle_monitor/MapEngine_data/track_record_data/DF/stop_{0}_{1}_{2}_{3}.txt".format(
        subFloat(floatStartX), subFloat(floatStartY), subFloat(floatEndX), subFloat(floatEndY))
    ret = 0
    rospy.logdebug("strFileName1:{0}".format(strFileName1))
    rospy.logdebug("strFileName2:{0}".format(strFileName2))
    if os.path.exists(strFileName1) and os.path.exists(strFileName2):
        ret = 0
    else:
        ret = -1
    return ret


def call_process(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, strTrajUrlDpqg, strTrajMd5Dpqp,
                 strStopUrlDpqp, strStopMd5Dpqp, timestampDpqp, floatStartX, floatStartY, floatEndX, floatEndY):
    intFlagPriorityFirst = 0

    intResultPriorityFirst = 0

    intResultPriorityFirst_XY = 0

    intFlagPrioritySecond = 0

    intResultPrioritySecond = 0

    intResultPrioritySecond_XY = 0
    intLastStatus = -1
    intShouldCheckV250 = 0
    try:
        intResultPriorityFirst = processFileV260(lLineId, strTrajUrlDpqg, strTrajMd5Dpqp, strStopUrlDpqp,
                                                 strStopMd5Dpqp, timestampDpqp, floatStartX, floatStartY, floatEndX,
                                                 floatEndY)
        if intResultPriorityFirst == -1 or intResultPriorityFirst == 9:
            intShouldCheckV250 = 1
        else:
            intShouldCheckV250 = 0
            intLastStatus = intResultPriorityFirst

        if intShouldCheckV250 == 1:
            intResultPrioritySecond = processFileV250(lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5,
                                                      timestamp, floatStartX, floatStartY, floatEndX, floatEndY)
            rospy.logdebug("==== intResultPrioritySecond:{0}".format(intResultPrioritySecond))
            intLastStatus = intResultPrioritySecond
        if intResultPriorityFirst == -1 and intResultPrioritySecond == -1:
            intLastStatus = 8

        rospy.logdebug(
            "=============intResultPriorityFirst:{0},intResultPrioritySecond:{1}".format(intResultPriorityFirst,
                                                                                         intResultPrioritySecond))

        pbSend = common_trajectory_agent_sync_status_pb2.TrajectoryAgentSyncStatus()
        pbSend.header.seq = 1
        pbSend.header.stamp.sec = rospy.Time.now().secs
        pbSend.header.stamp.nsec = rospy.Time.now().nsecs
        pbSend.header.frame_id = "trajectory_agent_frame_id"
        pbSend.header.module_name = "trajectory_agent"

        pbSend.sync_status = intLastStatus
        rospy.logdebug("================================= pbSend.sync_status:{0},msg:{1}".format(intLastStatus,
                                                                                                 globalErrorCodeMsg[
                                                                                                     intLastStatus]))

        strBuffer = pbSend.SerializeToString()
        rosMessage = BinaryData()
        rosMessage.data = strBuffer
        rosMessage.size = len(strBuffer)
        globalPubToSystemMasterStatus.publish(rosMessage)
        # global globalDictTaskRunningStatus
        # if globalDictTaskRunningStatus == (int(lLineId)):
        #     print "success delete key from  globalDictTaskRunningStatus: {0}".format(int(lLineId))
        #     globalDictTaskRunningStatus = -1
        #     print "now  display globalDictTaskRunningStatus:{0}".format(globalDictTaskRunningStatus)


    except Exception as e:
        rospy.logwarn('repr(e):{0}'.format(repr(e)))
        rospy.logwarn('e.message:{0}'.format(e.message))
        rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))


class TrajectoryImpInterfaceDataSource(InterfaceDataSource):
    strUrlList = None
    strUrlSync = None
    mScheduler = None
    mEnumDataSourceType = None
    mCacheUtils = None
    mStrConfigFileName = None
    mCommonPara = None
    mInterVal = None

    def __init__(self):
        self.strUrlList = "https://mdev.zhidaohulian.com/config/file/list"
        self.strUrlSync = "https://mdev.zhidaohulian.com/config/file/sync"
        self.mEnumDataSourceType = EnumDataSourceType.DATA_SOURCE_UPDATE_CONFIG
        self.mStrConfigFileName = "/home/mogo/data/TrajectoryConfigCache.json"
        self.mCommonPara = CommonPara()
        self.mCommonPara.initPara()
        self.mInterVal = 120

    def setScheduler(self, instanceScheduler):
        self.mScheduler = instanceScheduler

    def setCacheUtils(self, instanceCacheUtil):
        self.mCacheUtils = instanceCacheUtil

    def getModuleName(self):
        return "trajectory"

    def getVersion(self):
        pass

    def configure(self):
        strConfigFilePath = "/home/mogo/data/TrajectoryConfig.json"
        intError = 0
        dictConfig = {}
        intError, dictConfig = instanceReadConfigFile.readJsonConfig(strConfigFilePath)
        if intError == 0 and len(dictConfig) > 0:
            if dictConfig.has_key("url_list"):
                self.strUrlList = dictConfig['url_list']
            if dictConfig.has_key("url_sync"):
                self.strUrlSync = dictConfig['url_sync']
        return intError

    def init_module(self):
        self.setScheduler(instanceScheduler)
        self.setCacheUtils(instanceCacheUtils)

    def destroy_module(self):
        pass

    def transaction(self, msg):
        rospy.logdebug(
            "--------------------------------------------------recv from channel /trajectory_agent/cmd/transaction ")
        # global globalDictTaskRunningStatus
        if msg.size > 0:
            pbLine = common_message_pad_pb2.TrajectoryDownloadReq()
            pbLine.ParseFromString(msg.data)
            # parse pb msg
            lLineId = pbLine.line.lineId
            strTrajUrl = pbLine.line.trajUrl
            # print "type:{0}".format(type(pbLine.line.trajMd5))
            strTempTrajMd5 = str(pbLine.line.trajMd5)
            strTrajMd5 = strTempTrajMd5
            strStopUrl = pbLine.line.stopUrl
            strTempStopMd5 = str(pbLine.line.stopMd5)
            strStopMd5 = strTempStopMd5
            timestamp = pbLine.line.timestamp

            ## Dpqg  traj
            strTrajUrlDpqg = pbLine.line.trajUrl_dpqp
            strTrajMd5Dpqp = str(pbLine.line.trajMd5_dpqp)
            strStopUrlDpqp = pbLine.line.stopUrl_dpqp
            strStopMd5Dpqp = str(pbLine.line.stopMd5_dpqp)
            timestampDpqp = pbLine.line.timestamp_dpqp

            floatStartX = float(0.0)
            floatStartY = float(0.0)
            floatEndX = float(0.0)
            floatEndY = float(0.0)
            rospy.logdebug(
                "call_process: recv  lLineId:{0}, strTrajUrl:{1}, strTrajMd5:{2}, strStopUrl:{3},strStopMd5:{4}," \
                "timestamp:{5},strTrajUrlDpqg:{6},strTrajMd5Dpqp:{7},strStopUrlDpqp:{8},strStopMd5Dpqp:{9}," \
                "timestampDpqp:{10}".format(
                    lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5, timestamp, strTrajUrlDpqg, strTrajMd5Dpqp,
                    strStopUrlDpqp, strStopMd5Dpqp, timestampDpqp))
            globalProcessRequestPool.submit(call_process, lLineId, strTrajUrl, strTrajMd5, strStopUrl, strStopMd5,
                                            timestamp, strTrajUrlDpqg, strTrajMd5Dpqp, strStopUrlDpqp, strStopMd5Dpqp,
                                            timestampDpqp, floatStartX, floatStartY, floatEndX, floatEndY)

    def checktrajstate(self, msg, refJob):
        pass

    def process_topic(self, strTopicName, msg):
        print "------enter---process_topic: strTopicName:{0} =========".format(strTopicName)
        while True:
            if strTopicName == "/trajectory_agent/cmd/transaction":
                self.transaction(msg)
                break
            if strTopicName == "/trajectory_agent/cmd/checktrajstate":
                self.checktrajstate(msg)
                break
            break
        pass

    def process_cycle(self, dictParameter):
        pass

    def process_startup(self, dictParameter):
        pass

    def getNeedUpdateFile(self, refJob):
        intError = 0
        if len(refJob) == 0:
            intError = -1
        else:
            instanceCommonUtils.compareJobVersion(refJob, self.mCacheUtils)
        return intError

    def pushJobScheduler(self, refDataSource, refJob):
        refJob[0].enumJobType = EnumJobType.JOB_TYPE_IMMEDIATELY
        refJob[0].handlerDataSource = self
        self.mScheduler.add_job_to_queue(refDataSource, refJob)

    def schedulerFinishAction(self, refJob):
        self.checkAtomicFeature(refJob)
        self.install_stage_path(refJob)
        self.install_dst_path(refJob)
        self.write_cache_file(refJob)
        self.notify_pad(refJob)
        self.notify_cloud(refJob)
        self.write_event(refJob)

    def checkAtomicFeature(self, refJob):

        pass

    def install_stage_path(self, refJob):
        # for idx in range(len(refJob.listJobCollect)):
        #     shutil.copyfile(refJob.listJobCollect[idx].strFullFileTempName,
        #                     refJob.listJobCollect[idx].strFullFileStageName)
        pass

    def install_dst_path(self, refJob):
        for idx in range(len(refJob.listJobCollect)):
            shutil.copyfile(refJob.listJobCollect[idx].strFullFileTempName,
                            refJob.listJobCollect[idx].strFullFileName)
        pass

    def write_cache_file(self, refJob):
        for idx in range(len(refJob.listJobCollect)):
            intLocalModifyTimeStamp = int(os.path.getmtime(refJob.listJobCollect[idx].strFullFileName))
            strUrl = refJob.listJobCollect[idx].strUrl
            strMd5 = refJob.listJobCollect[idx].strMd5
            intPublishTimestamp = refJob.listJobCollect[idx].intPublishTimeStamp
            self.mCacheUtils.writeFileCacheInfo(self.mStrConfigFileName, strUrl, strMd5, intPublishTimestamp,
                                                intLocalModifyTimeStamp)

    def notify_pad(self, refJob):
        pass

    def notify_cloud(self, refJob):
        pass

    def write_event(self, refJob):
        pass

    def getTimeval(self):
        return self.mInterVal
