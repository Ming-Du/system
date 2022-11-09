#!/usr/bin/env python
import logging
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d]' '- %(levelname)s: %(message)s',level=logging.INFO)
logging.debug('debug message')


class InterfaceDataSource:

    def getModuleName(self):
        pass

    def getVersion(self):
        pass

    def configure(self):
        pass

    def init_module(self):
        pass

    def destroy_module(self):
        pass

    def process_topic(self, strTopicName, msg):
        pass

    def process_cycle(self,dictParameter):
        pass

    def process_startup(self,dictParameter):
        pass

    def getNeedUpdateFile(self, refJob):
        pass

    def pushJobScheduler(self, refDataSource, refJob):
        pass

    def schedulerFinishAction(self, refJob):
        pass

    def checkAtomicFeature(self, refJob):
        pass

    def install_stage_path(self, refJob):
        pass

    def install_dst_path(self, refJob):
        pass

    def write_cache_file(self, refJob):
        pass

    def notify_pad(self, refJob):
        pass

    def notify_cloud(self, refJob):
        pass

    def write_event(self, refJob):
        pass

    def getTimeval(self):
        pass

    def setScheduler(self, instanceScheduler):
        pass

    def setCacheUtils(self, instanceCacheUtil):
        pass

    def relink(self):
        pass