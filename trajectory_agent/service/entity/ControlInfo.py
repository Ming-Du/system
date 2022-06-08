#!/usr/bin/env python
class ControlInfo:
    lineId = None
    strTrajUrl = None
    strTrajMd5 = None
    strStopUrl = None
    strStopMd5 = None
    timestamp = None
    strVehicleModel = None
    strMsgType = None
    strStartName = None
    strEndName = None
    strStartLatLon = None
    strEndLatLon = None

    def __init__(self):
        self.lineId = -1
        self.strTrajUrl = ""
        self.strTrajMd5 = ""
        self.strStopUrl = ""
        self.strStopMd5 = ""
        self.timestamp = 0
        self.strVehicleModel = ""
        self.strMsgType = ""
        self.strStartName = ""
        self.strEndName = ""
        self.strEndLatLon = ""
        self.strEndLatLon = ""
        pass
