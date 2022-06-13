#!/usr/bin/env python
# coding=utf-8

import re
from sys_common import ssh_command
from sys_globals import SysCmd_to_Agent


def get_version_of_map():
    """
    #@name: 
    #@msg: get version string need [ Version:MAP-taxi_RoboTaxi_Default_2.4.0.2_27_logResove_20220527 ]
    #@return {*}
    """

    ret = 'unknow'
    cmd = SysCmd_to_Agent.Get_MAP_Version
    status, results = ssh_command(SysCmd_to_Agent.g_agent_mogo_pwd, cmd)
    
    if status or not results:
        print('cmd result:', status, results)
        return ret

    for line in results.split('\n'):
        if 'Version' == line.split(':')[0]:
            ver = re.search("(\d+)(\.\d+){1,3}",  line.split(':')[1])
            if ver:
                major = int(ver.group()[0])
                minor = int(ver.group()[2])
                if major >= 2 and minor > 4:
                    ret = '250'
                else:
                    ret = ver.group()
                break

    return ret


if __name__ == '__main__':
    ver=get_version_of_map()
    print (ver)