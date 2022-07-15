#!/usr/bin/env python
#_*_coding:utf-8 _*_ 
import json
import sys
import os
from rospkg import RosPack
# from roslaunch import mogo_msg

def main(vehicle_type,host,xavier_type,type):
    # mogo_log = mogo_msg.MOGO_MSG(ID="%s[%s]"%(__file__,host))
    # mogo_log.init()
    launch_files = []
    # other_launch_files = []
    with open(os.path.join(RosPack().get_path('launch'),'config/launch_config.json'),'r') as f:
        file_list = json.load(f).get('file_list')
        for it in file_list:
            try:
                # 跳过本机不启动的
                machine_list = it.get('machine').get(vehicle_type).get(xavier_type)
                if machine_list.count(host) == 0:
                    continue

                # 筛选指定type:MAP SYS
                if it.get('type') != type:
                    continue
                file_name = it.get('name')
                package = it.get('package')
                path = it.get('path')
                # package和path都未指定,使用当前路径的.launch
                if not package and not path:
                    launch_files.append(file_name)
                # 指定了package和path,且path是相对路径(不以'/'开头),则使用package所在路径加path路径的中的.launch
                elif package and path:
                    if path[:1] != '/':
                        try:
                            launch_files.append(os.path.join(RosPack().get_path(str(package)),path,file_name))
                        except:
                            # 找不到package则只是用path路径
                            launch_files.append(os.path.join(path,file_name))
                    elif path[:1] == '/': # path为绝对路径则优先使用path路径
                        launch_files.append(os.path.join(path,file_name))
                elif package and not path:
                    launch_files.append('%s %s'%(package,file_name))
                else:
                    launch_files.append(os.path.join(path,file_name))
            except:
                continue

    with open(os.path.join(RosPack().get_path('launch'),'config/%s_%s_%s_%s.list'%(type,vehicle_type,host,xavier_type)),'w') as f:
        f.writelines(map(lambda x : x + '\n', launch_files))

if __name__ == '__main__':
    vehicle_type,host,xavier_type,type = sys.argv[1:]
    main(vehicle_type,host,xavier_type,type)
                
