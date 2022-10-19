#!/usr/bin/env python
import EnumVersion


class JobItem:
    strFullFileName = None
    strFullFileStageName = None
    strFullFileTempName = None
    strUrl = None
    strMd5 = None
    intReplyId = None
    strXiverInfo = None
    intPublishTimeStamp = None
    intStatus = None
    strAtomicId = None
    strVersionMap = None
    strVehicleType = None
    strLinkPath = None
    eVersion = None

    def __init__(self):
        self.strFullFileName = ""
        self.strFullFileStageName = ""
        self.strFullFileTempName = ""
        self.strUrl = ""
        self.strMd5 = ""
        self.intReplyId = 0
        self.strXiverInfo = ""
        self.intPublishTimeStamp = 0
        self.intStatus = 0
        self.strAtomicId = ""
        self.strVersionMap = ""
        self.strVehicleType = ""
        self.strLinkPath = ""
        self.eVersion = EnumVersion.EnumVersion.INIT_VERSION

        pass
