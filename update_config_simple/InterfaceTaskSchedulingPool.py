#!/usr/bin/env python
import logging
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d]' '- %(levelname)s: %(message)s',level=logging.INFO)
logging.debug('debug message')


class InterfaceTaskSchedulingPool():

    def getVersion(self):
        pass

    def configure(self):
        pass

    def init_module(self):
        pass

    def destroy_module(self):
        pass

    def register_executor(self, instanceExecutor):
        pass

    def add_job_to_queue(self, instanceInterfaceDataSource, instanceJob):
        pass

    def action_autopilot_status_change(self, intPilotMode):
        pass

    def changeJobStatus(self, instanceJob):
        pass

    def scheduler_again(self):
        pass
