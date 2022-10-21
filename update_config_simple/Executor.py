#!/usr/bin/env python
import commands
import os
import signal
import traceback
from Job import Job
import rospy
from JobItem import JobItem
from EnumJobStatus import EnumJobStatus


class Executor:
    intCurrentJobId = None
    dictRunningWgetPid = None
    mJob = None

    def __init__(self):
        self.intCurrentJobId = 0
        self.dictRunningWgetPid = {}

    def run_executor_job(self, instanceJob):
        rospy.loginfo("---------------run_executor_job active------------------")
        try:
            intCurrentJobId = instanceJob.strJobId
            rospy.loginfo("##########   intCurrentJobId:{0}".format(intCurrentJobId))
            self.mJob = instanceJob
            listTemp = instanceJob.listJobCollectUpdate
            rospy.loginfo("############# run_executor_job: listTemp:{0}".format(listTemp))
            for idx in range(len(listTemp)):
                if len(listTemp[idx].strFullFileTempName) > 0:
                    strFolderName = os.path.dirname(listTemp[idx].strFullFileTempName)
                    print "================== strFolderName:{0}".format(strFolderName)
                    if os.path.exists(strFolderName):
                        pass
                    else:
                        os.makedirs(strFolderName)
                        os.chmod(strFolderName, 0777)
                    if os.path.exists(listTemp[idx].strFullFileTempName):
                        os.remove(listTemp[idx].strFullFileTempName)
                    strCmd = "curl -o  '{0}'  '{1}'  ".format(listTemp[idx].strFullFileTempName, listTemp[idx].strUrl)
                    os.system(strCmd)
                else:
                    rospy.loginfo("------------------------ ignore: {0}".format(listTemp[idx].strFullFileTempName))
                # self.create_task(listTemp[idx].strUrl, listTemp[idx].strFullFileTempName)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def getCurrentExecutorRunningJob(self):
        return self.mJob

    def stop_current_executor_job(self, instanceJob):
        try:
            for k, v in self.dictRunningWgetPid.items():
                os.kill(k, signal.SIGCHLD)
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))

    def create_task(self, strUrl, strTempFileName):
        ret = None
        strTempFileName = None
        try:
            rospy.loginfo("============= create_task process url:{0},strTempFileName:{1}".format(strUrl, strTempFileName))
            strDirName = os.path.dirname(strTempFileName)
            if os.path.exists(strDirName):
                pass
            else:
                os.makedirs(strDirName)
                os.chmod(strDirName, 0777)

            ret = 0
            status = 0
            pid = os.fork()
            while True:
                # if len(self.dictRunningWgetPid) > 0:
                #     print("len(self.dictRunningWgetPid) > 0 ")
                #     break
                if pid < 0:
                    rospy.logdebug("self.intCurrentJobId < 0 ")
                    status = -1
                    break
                if pid > 0:
                    rospy.logdebug("parent process ")
                    self.dictRunningWgetPid[pid] = pid
                    rospy.logdebug("====register sub process_pid:{0}".format(self.dictRunningWgetPid))
                    #  os.waitpid(pid, 0)
                    # if self.dictRunningWgetPid.has_key(pid):
                    #     del self.dictRunningWgetPid[pid]
                    #     self.mJob = None
                    #     self.mJob.enumStatus = EnumJobStatus.EnumJobStatus.JOB_STATUS_FINISH
                    rospy.logdebug("====after finish wget dictRunningWgetPid:{0}".format(self.dictRunningWgetPid))
                    status = 0
                    break
                if pid == 0:
                    rospy.logdebug("====sub process")
                    os.execl("/usr/bin/wget", "/usr/bin/wget", "--limit-rate=10M", "--connect-timeout=5",
                             "--dns-timeout=5", "-c", strUrl, "-O", strTempFileName)
                    break
                break

                ret = status
        except Exception as e:
            rospy.logwarn('repr(e):{0}'.format(repr(e)))
            rospy.logwarn('e.message:{0}'.format(e.message))
            rospy.logwarn('traceback.format_exc():%s' % (traceback.format_exc()))
            ret = -1
        return ret, strTempFileName
