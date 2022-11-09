#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum


class EnumJobStatus(Enum):
    JOB_STATUS_INIT = 0
    JOB_STATUS_RUNNING = 1
    JOB_STATUS_PAUSE = 2
    JOB_STATUS_WAITING_RESOURCE = 3
    JOB_STATUS_FINISH = 4
