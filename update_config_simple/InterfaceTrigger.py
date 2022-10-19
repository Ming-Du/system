#!/usr/bin/env python
import logging
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d]' '- %(levelname)s: %(message)s',level=logging.INFO)
logging.debug('debug message')


class InterfaceTrigger():
    def getVersion(self):
        pass

    def configure(self):
        pass

    def init_module(self):
        pass

    def destroy(self):
        pass

    def addNotifyDataSourceModule(self, instanceInterfaceDataSource):
        pass

    def addNotifyTaskSchedulerPool(self, instanceInterfaceTrigger):
        pass

    def notifyDataSourceModule(self):
        pass

    def notifySchedulerPool(self):
        pass

    def processPilotUpdate(self):
        pass

    def processTopicInfo(self, pbTopicInfo):
        pass

    def start_loop_internal_timer(self):
        pass
