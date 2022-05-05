import collections
import commands


class NetTools:
    dictNetInfo = None

    def __init__(self):
        self.dictNetInfo = {}

    def getIp(self, strNetCardName):
        strIpResult = ""
        strGetIpCmd = "ifconfig %s  | grep netmask | awk '{print $2}'" % (strNetCardName)
        (status, strTempResult) = commands.getstatusoutput(strGetIpCmd)
        while True:
            if status == 0:
                strIpResult = strTempResult
                break
            if status != 0:
                print "get Ip failed"
                break
            break
        print strIpResult
        print type(strIpResult)
        if len(strIpResult) > 0:
            self.dictNetInfo["ip"] = strIpResult

    def getMac(self, strNetCardName):
        strMacResult = ""
        strGetMacCmd = "ifconfig %s  | grep ether | awk  '{print $2}'" % strNetCardName
        (status, strTempResult) = commands.getstatusoutput(strGetMacCmd)
        while True:
            if status == 0:
                strMacResult = strTempResult
                break
            if status != 0:
                print "get Ip failed"
                break
            break
        print strGetMacCmd
        print type(strGetMacCmd)
        if len(strGetMacCmd) > 0:
            self.dictNetInfo['mac'] = strMacResult

    def envInit(self, strNetCardName):
        self.getIp(strNetCardName)
        self.getMac(strNetCardName)
        return self.dictNetInfo
