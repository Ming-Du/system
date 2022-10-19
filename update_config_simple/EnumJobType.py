#!/usr/bin/env python

from enum import Enum


class EnumJobType(Enum):
    JOB_TYPE_INIT = 0
    JOB_TYPE_IMMEDIATELY = 1
    JOB_TYPE_DELAY = 2