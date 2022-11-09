#!/usr/bin/env python
import os.path

strFileName = "/home/mogo/data/vehicle_monitor/slinks.cfg"
listContent = None
while True:
    if not os.path.exists(strFileName):
        break
    if os.path.exists(strFileName):
        with open(strFileName, "r") as f:
            strContent = f.read()
            print "strContent:{0}".format(strContent)
            listContent = strContent.splitlines()
        break
    break
for idx in range(len(listContent)):
    print "##############  line:{0}".format(listContent[idx])
    if len(listContent[idx]) > 0:
        listUnit = str(listContent[idx]).split(':')
        if len(listUnit) == 2:
            print "----------   {0} link to  {1}".format(listUnit[0], listUnit[1])

