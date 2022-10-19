#!/usr/bin/env python

from enum import Enum


class EnumDataSourceType(Enum):
    DATA_SOURCE_UPDATE_CONFIG = 0
    DATA_SOURCE_AI_MODEL = 1
    DATA_SOURCE_SLAM_MAP = 2
    DATA_SOURCE_HD_MAP_AGENT = 3
    DATA_SOURCE_TRAJECTORY_AGENT = 4
