#!/usr/bin/env python

from __future__ import print_function

import optparse
import os
import shutil
import signal
import subprocess
import sys
import time
try:
    from UserDict import UserDict  # Python 2.x
except ImportError:
    from collections import UserDict  # Python 3.x

import roslib.message
import roslib.packages

#from bag import Bag, Compression, ROSBagException, ROSBagFormatException, ROSBagUnindexedException, ROSBagEncryptNotSupportedException, ROSBagEncryptException
#from migration import MessageMigrator, fixbag2, checkbag

from rosnode import *


def get_topics_by_machine(machine_name):
    pubs = []
    master = rosgraph.Master(ID)
    try:
        state = master.getSystemState()
        print(state)
    except socket.error:
        raise ROSNodeIOException("Unable to communicate with master!")
    local_nodes = get_nodes_by_machine(machine_name)
    print (local_nodes)
    for node in local_nodes:
        pubs += [t for t ,l in state[0] if node in l and 'clock' not in t and 'rosout' not in t]
    pubs = list(set(pubs))
    print("*******************")
    print(pubs)
    print("*******************")
    return pubs

def gethosttopics():
    rosmachine = os.getenv('ROS_HOSTNAME')
    if rosmachine == None:
        print("ROS_HOSTNAME not exist")

    topics = get_topics_by_machine(rosmachine)
    if len(topics) == 0:
        print("%s has not publicated any topics"%(rosmachine))
    return  topics

#if __name__ =="__main__":
#    record_cache_main(sys.argv);

