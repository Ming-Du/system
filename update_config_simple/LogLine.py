#!/usr/bin/env python
import sys


def LogLine(msg):
    print('Print Message: ' + msg + ' ,File: "' + __file__ + '", Line ' + str(
        sys._getframe().f_lineno) + ' , in ' + sys._getframe().f_code.co_name)


