import commands
import json
import traceback
from entity.CommonPara import CommonPara
import os


class GenLaunchList:
    globalCommonPara = None
    strTempLaunchListFolder = ""
    dictHostNameMapList = {}

    def __init__(self):
        self.globalCommonPara = CommonPara()
        self.globalCommonPara.initPara()
        self.strTempLaunchListFolder = "/tmp/monitor_process/"

    def getXiverType(self):
        XiverType = "6x"
        if os.path.exists("/etc/hosts"):
            strCmdCheckMultiXiver = "cat  /etc/hosts | grep slave | wc -l"
            try:
                (status, output) = commands.getstatusoutput(strCmdCheckMultiXiver)
                if status == 0:
                    print "output:{0}".format(output)
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
        print "=============== XiverType:{0}".format(XiverType)
        return XiverType

    def getCarType(self):
        strCarType = "jinlv"
        try:
            while True:
                print self.globalCommonPara.dictCarInfo
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
        print "=============== strCarType:{0}".format(strCarType)
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

        try:
            dictContent = json.loads(strContent)
            dictNodeList = dictContent['file_list']
            fileLength = len(dictNodeList)
            if not os.path.exists(self.strTempLaunchListFolder):
                os.makedirs(self.strTempLaunchListFolder)
            if os.path.exists("{0}rosmaster.list".format(self.strTempLaunchListFolder)):
                os.remove("{0}rosmaster.list".format(self.strTempLaunchListFolder))

            if os.path.exists("{0}rosslave.list".format(self.strTempLaunchListFolder)):
                os.remove("{0}rosslave.list".format(self.strTempLaunchListFolder))

            if os.path.exists("{0}rosslave-103.list".format(self.strTempLaunchListFolder)):
                os.remove("{0}rosslave-103.list".format(self.strTempLaunchListFolder))

            if os.path.exists("{0}rosslave-104.list".format(self.strTempLaunchListFolder)):
                os.remove("{0}rosslave-104.list".format(self.strTempLaunchListFolder))

            if os.path.exists("{0}rosslave-105.list".format(self.strTempLaunchListFolder)):
                os.remove("{0}rosslave-105.list".format(self.strTempLaunchListFolder))

            if os.path.exists("{0}rosslave-106.list".format(self.strTempLaunchListFolder)):
                os.remove("{0}rosslave-106.list".format(self.strTempLaunchListFolder))

            if os.path.exists("{0}rosslave-107.list".format(self.strTempLaunchListFolder)):
                os.remove("{0}rosslave-107.list".format(self.strTempLaunchListFolder))


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

        for elem_node in dictNodeList:
            print "========================="
            try:
                print elem_node['package']
                print elem_node['name']
                lineContent = "{0} {1}".format(elem_node['package'], elem_node['name'])
                list_xiver = elem_node['machine'][strCarType][strXiverType]
                for elem_machine in list_xiver:
                    print elem_machine
                    strListFileName = "{0}{1}.list".format(self.strTempLaunchListFolder, elem_machine)
                    self.dictHostNameMapList[elem_machine] = strListFileName
                    with open(strListFileName, "a+") as f_list:
                        f_list.write(lineContent)
                        f_list.write('\n')
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
        if len(self.dictHostNameMapList) > 0:
            print json.dumps(self.dictHostNameMapList)

    def getLaunchFilePath(self, strMachineName):
        strFilePath = ""
        dictErrorCode = {}
        dictErrorCode[0] = "success"
        dictErrorCode[-1] = "fail"
        dictErrorCode[-2] = "key not exists"
        strErrorMsg = ""
        ret = -1
        try:
            while True:
                if len(strMachineName) == 0:
                    ret = -1
                    break
                if len(self.dictHostNameMapList) == 0:
                    ret = -2
                    break
                if not self.dictHostNameMapList.has_key(strMachineName):
                    ret = -2
                    break
                strFilePath = self.dictHostNameMapList[strMachineName]
                ret = 0
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
        strErrorMsg = dictErrorCode[ret]
        return strFilePath, ret, strErrorMsg


# instanceGenLaunchList = GenLaunchList()
# instanceGenLaunchList.initData()
# strFileName, ret, strErrorMsg = instanceGenLaunchList.getLaunchFilePath("rosmaster")
# print "=========== strFileName:{0}, ret:{1},strErrorMsg:{2}".format(strFileName,ret,strErrorMsg)