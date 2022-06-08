#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import json
import time
import threading
import copy

## local config file
from config import node_config

###### ros module
import rospy

###### mogo msg
from proto import common_log_reslove, system_pilot_mode_pb2
from autopilot_msgs.msg import BinaryData

##### file async handle
import asyncio
#import aiofiles


## constants
work_dir = "/home/mogo/data/log"
output_dir = os.path.join(work_dir, "ROS_STAT_RESULT")
# output_topic_hz_path = os.path.join(output_dir, "topic_hz")
input_dir = os.path.join(work_dir, "ROS_STAT" ,"EXPORT")
tmp_dir = os.path.join(work_dir, "ROS_STAT_TMP")
output_path = os.path.join(output_dir, "topic_stat")


## globals
g_pilot_mode = 0
car_info = {}

# handle_rate = 1     # 日志过大时切分处理
handle_index = -1
last_timestamp = 0  # 清理已处理过的msg
all_pub_msg = {}
all_sub_msg = {}
node_callback_history = {}  # {tpoic:one_log}
all_man_tag_beg = {}     # tag: one_log
all_man_tag_end = {}   # {tag: {stamp: one_log}


all_topic_hz_info = dict()  # k=name, v={dst_node:[list], start_time:t1, end_time:t2 pub:num max_delay:usec}
g_topic_hz_handler = None

g_time_split_threshold = 5  # sec
g_time_start_value = time.time()
g_time_split_value = time.time()
g_time_split_end = time.time()

# the follow used for test
g_test_mode = True   # default set False
log_exceptions_dict = dict()   # k=node_name, v={ topic_name : error_num }    # used for no seq log record


## utils
def get_time_used(func):
    def wrapper(*args,**kwargs):
        start_time=time.time()
        ret = func(*args,**kwargs)
        end_time=time.time()
        if g_test_mode or 1 < end_time - start_time:
            print('{} used time is {}'.format(func.__name__, end_time-start_time))
        return ret
    return wrapper


class TopicHZ():
    """
    create for topic hz pub
    """
    def __init__(self):
        self.set_topic_hz_pub = rospy.Publisher('/autopilot_info/internal/report_topic_hz', BinaryData, queue_size=10)
        self.log_pub_msg = None

    def pub_topic_hz_info(self):
        '''
        pub topic hz info
        '''
       
        log_pub_msg_str = self.log_pub_msg.SerializeToString()
        topic_hz_msg = BinaryData()

        topic_hz_msg.header.seq         = 1
        topic_hz_msg.header.stamp.secs   = rospy.rostime.Time.now().secs
        topic_hz_msg.header.stamp.nsecs  = rospy.rostime.Time.now().nsecs
        topic_hz_msg.header.frame_id    = "log_reslove_frame_id"
        topic_hz_msg.name = "log_reslove"
        topic_hz_msg.size = len(log_pub_msg_str)
        topic_hz_msg.data = log_pub_msg_str
        self.set_topic_hz_pub.publish(topic_hz_msg)

        #for test parse
        if g_test_mode:
            test_topic_hz = common_log_reslove.PubLogInfo()
            test_topic_hz.ParseFromString(topic_hz_msg.data)
            for one_topic_hz in test_topic_hz.topic_hz:
                print(one_topic_hz.name)
                print(one_topic_hz.hz)
                print(one_topic_hz.max_delay)

    def analyse_all_topic(self):
        '''
        analyse data from  all_topic_hz_info
        '''
        log_pub_msg = None
        try:
            log_pub_msg = common_log_reslove.PubLogInfo()
            log_pub_msg.header.seq         = 1
            log_pub_msg.header.stamp.sec   = rospy.rostime.Time.now().secs
            log_pub_msg.header.stamp.nsec  = rospy.rostime.Time.now().nsecs
            log_pub_msg.header.frame_id    = "log_reslove_frame_id"
            log_pub_msg.header.module_name = "log_reslove"
            log_pub_msg.start_stamp = 0
            log_pub_msg.end_stamp = 0
            for name, info in all_topic_hz_info.items():
                if info['end_time'] == info['start_time']:
                    continue
                # print("get topic is {}, info {}".format(name, info))
                hz_num = int(info["num"] / ((info['end_time']-info['start_time'])/1000000000))
                topic_hz = log_pub_msg.topic_hz.add()
                topic_hz.name = name
                topic_hz.hz = hz_num
                topic_hz.max_delay = int(info['max_delay']/1000000)  # msec
                # clear data for next time used
                all_topic_hz_info[name]['start_time'] = all_topic_hz_info[name]['end_time'] 
                all_topic_hz_info[name]['num'] = 0
                all_topic_hz_info[name]['max_delay'] = 0  # get new max_delay every loop
        except Exception as e:
            print('There has some error:{}'.format(e))

        self.log_pub_msg = log_pub_msg
        return 

    @get_time_used
    def pub_topic_hz_once(self):
        self.analyse_all_topic()
        self.pub_topic_hz_info()


def set_car_info(data):
    data["code_version"] = car_info.get("code_version", "")
    data["carplate"] = car_info.get("carplate", "")
    data["cartype"] = car_info.get("cartype", "")

def read_car_info():
    try:
        with open("/autocar-code/project_commit.txt") as fp:
            contents = fp.read().split("\n")

        car_info["code_version"] = contents[1][len("Version:"):]
    except Exception as e:
        print('get code_version failed: {}'.format(e))
       
    try:
        with open("/home/mogo/data/vehicle_monitor/vehicle_config.txt") as fp:
            contents = fp.read().split("\n")

        plate = contents[0].split(":")[-1]
        car_info["carplate"] = plate.strip().strip("\"")
        brand = contents[1].split(":")[-1]      
        car_info["cartype"] = brand.strip().strip("\"")

    except Exception as e:
        print('get vehicle_config failed: {}'.format(e))

def add_log_to_topic_hz_dict(one):
    if one['topic'] not in all_topic_hz_info:
        all_topic_hz_info[one['topic']] = dict()
        all_topic_hz_info[one['topic']]['dst_node'] = list()
        all_topic_hz_info[one['topic']]['start_time'] = one['stamp']
        all_topic_hz_info[one['topic']]['end_time'] = one['stamp']
        all_topic_hz_info[one['topic']]['num'] = 0
        all_topic_hz_info[one['topic']]['max_delay'] = 0

    if one['link']['dst'] not in all_topic_hz_info[one['topic']]['dst_node']:
        all_topic_hz_info[one['topic']]['dst_node'].append(one['link']['dst'])
        
    if  one['stamp'] < all_topic_hz_info[one['topic']]['start_time']:
        ## the follow add for error record
        if g_test_mode:
            if one['node'] in log_exceptions_dict:
                if one['topic'] in log_exceptions_dict[one['node']]:
                    log_exceptions_dict[one['node']][one['topic']] += 1 
                else:
                    log_exceptions_dict[one['node']][one['topic']] = 1
            else:
                print('###topic:{}, pub_node:{} log save error! ### The case should not ingress!!!!!'.format(one['topic'], one['node']))
                log_exceptions_dict[one['node']] = dict()
                log_exceptions_dict[one['node']][one['topic']] = 1

    if one['stamp'] > all_topic_hz_info[one['topic']]['end_time']:
        if one['stamp'] - all_topic_hz_info[one['topic']]['end_time'] > all_topic_hz_info[one['topic']]['max_delay']:
            all_topic_hz_info[one['topic']]['max_delay'] = one['stamp'] - all_topic_hz_info[one['topic']]['end_time']
        all_topic_hz_info[one['topic']]['end_time'] = one['stamp']
        all_topic_hz_info[one['topic']]['num'] += 1   # same pub, the stamp is same


def update_one_log(one):
    global g_pilot_mode
       
    # 0是pub记录
    if one["type"] == 0:
        add_log_to_topic_hz_dict(one)

        if one["node"] not in node_config:
            return

        if one["topic"] != node_config[one["node"]]["pub"]:
            return

        if not g_test_mode and g_pilot_mode == 0:
            return

        if one["link"]["dst"] not in node_config:
            return

        one["uuid"] = one["header_stamp"]
        if one["uuid"] == 0:
            one["uuid"] = one["feature"]

        one["use_callback"] = []
        if len(node_config[one["node"]]["sub"]) == 0:
            one["no_callback"] = True
        
        for sub_topic in node_config[one["node"]]["sub"]:
            if sub_topic not in node_callback_history:
                if sub_topic != "":
                    #print("can not find sub {0}".format(sub_topic))
                    pass
            else:
                if node_callback_history[sub_topic]["thread"] != one["thread"]:
                    #print("pub/sub in different thread")
                    pass
                elif one["stamp"] - node_callback_history[sub_topic]["stamp"] > 10000000000 or one["stamp"] < node_callback_history[sub_topic]["stamp"]:
                    #print("mismatch sub")
                    pass
                else:
                    one["use_callback"].append(node_callback_history[sub_topic])

        if one["topic"] not in all_pub_msg:
            all_pub_msg[one["topic"]] = {}
        if one["uuid"] in all_pub_msg[one["topic"]]:
            #print("uuid exist")
            one["uuid_wrong"] = True

        if node_config[one["node"]].get('man_beg','') != '':
            tag = node_config[one["node"]].get('man_beg')
            if tag in all_man_tag_beg:
                one["use_beg_tag"] = all_man_tag_beg[tag]  # all beg and pub in same thread

        #放到all_pub里面
        all_pub_msg[one["topic"]][one["uuid"]] = one

    # 1是callback记录
    elif one["type"] == 1:
        if one["node"] not in node_config:
            return

        if not g_test_mode and g_pilot_mode == 0:
            return

        if one["topic"] not in node_config[one["node"]]["sub"]:
            return

        one["uuid"] = one["header_stamp"]
        if one["uuid"] == 0:
            one["uuid"] = one["feature"]

        # 只支持回溯一个
        node_callback_history[one["topic"]] = one

        if one["topic"] not in all_sub_msg:
            all_sub_msg[one["topic"]] = {}
        if one["uuid"] in all_sub_msg[one["topic"]]:
            #print("uuid exist")  dxc
            one["uuid_wrong"] = True
        all_sub_msg[one["topic"]][one["uuid"]] = one

    elif one["type"] == 2:
        if one["node"] not in node_config:
            return
        if one.get("tag",'') != node_config[one["node"]].get("man_beg","notag"):
            return

        if one["tag"] not in all_man_tag_beg:
            all_man_tag_beg[one["tag"]] = one

    elif one["type"] == 3:
        if one["node"] not in node_config:
            return
        if one.get("tag",'') != node_config[one["node"]].get("man_end","notag"):
            return

        one["uuid"] = one['ident'] or one['stamp'] # ident can match,but stamp may need find lately

        if one["tag"] not in all_man_tag_end:
            all_man_tag_end[one["tag"]] = {}
        if one["uuid"] in all_man_tag_end[one["tag"]]:
            #print("uuid exist")
            one["uuid_wrong"] = True
        
        all_man_tag_end[one["tag"]][one["uuid"]] = one  # only 2D_front used end, contact by ident
    else:
        return
    

''' begin used asyncio handle '''
async def load_remote_log(paths):
    """
    read remote log from paths which are named begin "remote"
    """
    global g_time_start_value
    global g_time_split_value

    handle_time = int(g_time_start_value%10000)
    remote_log_src=['102','103','104','105','106','107']
    
    while handle_time < int(g_time_split_value%10000):
        for src in remote_log_src:
            path_key=src+'_'+str(handle_time)
            for file_name in paths:            
                if path_key in file_name:
                    print(file_name)
                    with open(file_name, 'r') as fp:
                        contents = fp.read()
                        lines = contents.split("\n")
                        for line in lines:
                            start = line.find("#key-log#", 0, 128)
                            if start == -1:
                                continue
                            try:
                                one = json.loads(line[start+9:])
                                update_one_log(one)
                            except Exception as e:
                                print("the log {} in file {} is unexpect style! {}".format(line[start+9:], file_name, e))
                                continue                   
                            
        handle_time += 1
        await asyncio.sleep(0.1) 


async def load_log_by_time(filename):
    """
    read log info from local files which are named begin "ros_time"
    """
    global g_test_mode
    global g_time_start_value
    global g_time_split_value
    #print('filename is', filename)

    with open(filename, 'r') as fp:
        contents = fp.read()
        lines = contents.split("\n")

    for line in lines:
        sec_stamp = line.split('.')[0].split('[')[-1]
        if sec_stamp:
            if not g_test_mode and int(sec_stamp) < g_time_start_value: # alread handle
                continue
  
            if int(sec_stamp) < g_time_split_value:
                start = line.find("#key-log#", 0, 128)
                if start == -1:
                    await asyncio.sleep(0)
                    continue
                try:
                    one = json.loads(line[start+9:])
                    update_one_log(one)
                except Exception as e:
                    print("the log {} in file {} is unexpect style! {}".format(line[start+9:], filename, e))
                    continue               
                
            else:
                break
''' end used asyncio handle '''

''' handel file one by one '''
def load_one_log_by_time(ros_time_paths, remote_paths):
    global g_test_mode
    global g_time_start_value
    global g_time_split_value

    #print('ros_time={},remote={}'.format(ros_time_paths, remote_paths))
    #print('start_time={},split_time={}'.format(g_time_start_value,g_time_split_value))

    for path in ros_time_paths:
        with open(path, 'r') as fp:
            contents = fp.read()
            lines = contents.split("\n")

        for line in lines:
            sec_stamp = line.split('.')[0].split('[')[-1]
            if sec_stamp:
                if not g_test_mode and int(sec_stamp) < g_time_start_value: # alread handle
                    continue
    
                if int(sec_stamp) < g_time_split_value:
                    start = line.find("#key-log#", 0, 128)
                    if start == -1:
                        continue
                    try:
                        one = json.loads(line[start+9:])
                        update_one_log(one)
                    except Exception as e:
                        print("the log {} in file {} is unexpect style! {}".format(line[start+9:], path, e))
                        continue
                    
                else:
                    break
    
    handle_time = int(g_time_start_value%10000) if not g_test_mode else 0
    end_time = int(g_time_split_value%10000) if not g_test_mode else 9999
    remote_log_src=['102','103','104','105','106','107']

    while handle_time < end_time:
        for src in remote_log_src:
            path_key='{}_{}.log'.format(src, handle_time)
            for file_name in remote_paths:            
                if path_key in file_name:
                    # print(file_name)
                    with open(file_name, 'r') as fp:
                        contents = fp.read()
                        lines = contents.split("\n")
                        for line in lines:
                            start = line.find("#key-log#", 0, 128)
                            if start == -1:
                                continue
                            try:
                                one = json.loads(line[start+9:])
                                update_one_log(one)
                            except Exception as e:
                                print("the log {} in file {} is unexpect style! {}".format(line[start+9:], file_name, e))
                                continue
                        
        handle_time += 1


@get_time_used
def load_logs(input_paths):
    global handle_index
    global g_time_start_value
    global g_time_split_value
    global g_time_split_end
    global g_time_split_threshold

    if handle_index == -1:
        st_atime = int(time.time())
        st_mtime = 0
        for path in input_paths:
            stat = os.stat(path)
            if st_atime > stat.st_atime:
                st_atime = stat.st_atime
            if st_mtime <  stat.st_mtime:
                st_mtime = stat.st_mtime

        g_time_start_value = st_atime - 2  # before min access time 2 sec
        g_time_split_end = st_mtime
        if st_mtime - st_atime > g_time_split_threshold:   # log 1.7M/s  30s about 50M
            print('log save {} secs, more than {}, handle a part!'.format(st_mtime-st_atime, g_time_split_threshold) )
            g_time_split_value = st_atime + g_time_split_threshold
            handle_index = 0
        else:
            g_time_split_value = g_time_split_end
        
    if len(input_paths):
        ros_time_paths=[]
        remote_paths=[]
        for path in input_paths:
            if 'ros_time' in path:
                ros_time_paths.append(path)
            else:
                remote_paths.append(path)

        '''  used asyncio handle
        loop=asyncio.get_event_loop()
        tasks=[load_log_by_time(path) for path in ros_time_paths]
        tasks.append(load_remote_log(remote_paths))
        loop.run_until_complete(asyncio.wait(tasks))
        #loop.close()
        '''

        ''' handel file one by one '''
        load_one_log_by_time(ros_time_paths, remote_paths)

    # 分片处理流程
    if handle_index >= 0:
        # 如果处理完了，恢复全量处理
        if g_time_split_value >= g_time_split_end:
            handle_index = -1
        else:
            g_time_start_value = g_time_split_value
            g_time_split_value += g_time_split_threshold
            handle_index += 1


def analyze_outside_node(callback, data, record):
    if callback["topic"] not in all_pub_msg:
        #print("no topic")
        data["wrong"] = "on topic in pub"
        return

    if callback.get("uuid_wrong", False) == True:
        #print("uuid wrong 1")
        #print(callback)
        data["wrong"] = "uuid wrong"
        return

    if callback["uuid"] not in all_pub_msg[callback["topic"]]:
        #print("can not find pub")
        data["wrong"] = "can not find pub {0} {1}".format(callback["topic"], callback["uuid"])
        return

    pub = all_pub_msg[callback["topic"]][callback["uuid"]]
    if pub.get("uuid_wrong", False) == True:
        #print("uuid wrong 2")
        #print(pub)
        data["wrong"] = "uuid wrong"
        return

    ''' del by liyl
    use_time = round(float(callback["recv_stamp"] - pub["stamp"])/1000000, 2)
    wait_time = round(float(callback["stamp"] - callback["recv_stamp"])/1000000, 2)
    if use_time + wait_time > 20000:
        #print("pub-callback use time {0}".format(use_time))
        data["wrong"] = ">20000"
        return

    data["use_time"] += use_time + wait_time
    data["path"].append({"type":"pub_recv", "node":callback["node"], "use_time":use_time})
    data["path"].append({"type":"recv_call", "node":callback["node"], "use_time":wait_time})
    '''
    pub_recv_time = callback["recv_stamp"] - pub["stamp"]
    recv_call_time = callback["stamp"] - callback["recv_stamp"]
    data["use_time"] += pub_recv_time + recv_call_time
    if pub_recv_time + recv_call_time > 2*1000000000:
        data["wrong"] = ">2 sec"
        return
    data["path"].append({"type":"pub_recv", "node":callback["node"], "use_time":pub_recv_time})
    data["path"].append({"type":"recv_call", "node":callback["node"], "use_time":recv_call_time})

    analyze_inside_node(pub, data, record)

def analyze_inside_node(pub, data, record):
    if pub.get("no_callback", False) != False:
        if node_config[pub['node']].get("man_beg",'') != '':
            # add by liyil: man_beg -> pub
            # tag_name = node_config[pub['node']].get("man_beg")
            if 'use_beg_tag' in pub and pub.get('use_beg_tag',''):
                #beg = all_sub_msg[tag_name][pub['uuid']]
                beg = pub['use_beg_tag']
                beg_end_time = pub["stamp"] - beg["stamp"]
                u_spend = pub["utime"] - beg["utime"]
                s_spend = pub["stime"] - beg["stime"]
                w_spend = pub["wtime"] - beg["wtime"]
                idle_spend = beg_end_time - u_spend - s_spend - w_spend    
                u_percent, s_percent, w_percent, idle_percent = [round(x*1.0/beg_end_time,2) for x in (u_spend,s_spend,w_spend,idle_spend)]
                pdata["use_time"] += beg_end_time
                pdata["path"].append({"type": "beg_end", "node": pub["node"], "use_time": beg_end_time})
                pdata["path"].append({"type": "beg_end_cpu", "node": pub["node"], "u_spend": u_spend, "u_percent": u_percent, "s_spend": s_spend, "s_percent": s_percent, "w_spend": w_spend, "w_percent": w_percent, "idle_spend": idle_spend, "idle_percent": idle_percent})

        return

    if "use_callback" not in pub or len(pub["use_callback"]) == 0:
        #print("no use_callback")
        data["wrong"] = "can't find callback"
        return
    
    beg=None
    if 'use_beg_tag' in pub and pub.get('use_beg_tag',''):
        beg = pub['use_beg_tag']

    callback_size = len(pub["use_callback"])
    index = 0
    for callback in pub["use_callback"]:
        index += 1
        # 当多于一个path时，需添加新的data
        # 我们让最后一个sub路径直接用老data，之前的做深拷贝
        if index < callback_size:
            pdata = copy.deepcopy(data)
            record.append(pdata)
        else:
            pdata = data

        if callback_size > 1:
            pdata["split_path"].append(callback["topic"])

        if pub.get("uuid_wrong", False) == True or callback.get("uuid_wrong", False) == True:
            #print("uuid wrong 3")
            #print(pub)
            #print(callback)
            pdata["wrong"] = "uuid wrong"
            continue

        '''del by liyl
        use_time = round(float(pub["stamp"] - callback["stamp"])/1000000, 2)
        if use_time > 20000:
            #print("callback-pub use time {0}".format(use_time))
            pdata["wrong"] = ">20000"
            continue

        u_spend = round(float(pub["utime"] - callback["utime"])/1000000, 2)
        u_percent = round(float(u_spend / use_time), 2)
        s_spend = round(float(pub["stime"] - callback["stime"])/1000000, 2)
        s_percent = round(float(s_spend / use_time), 2)
        w_spend = round(float(pub["wtime"] - callback["wtime"])/1000000, 2)
        if w_spend > 20000:
            pdata["wrong"] = "w_spend>20000, cb tid:{} {} {}, pub tid:{} {} {}".format(callback["tid"], callback["thread"], callback["wtime"], pub["tid"], pub["thread"], pub["wtime"])
            continue
        #w_percent = round(float(w_spend / use_time), 2)
        #idle_spend = round(float(use_time - u_spend - s_spend - w_spend), 2)
        #idle_percent = round(float(idle_spend / use_time), 2)
        '''
        call_pub_time = pub["stamp"] - callback["stamp"]
        if call_pub_time > 2*1000000000:  # 2s
            #print("callback-pub use time {0}".format(use_time))
            pdata["wrong"] = ">2 sec"
            continue
        u_spend = pub["utime"] - callback["utime"]
        s_spend = pub["stime"] - callback["stime"]
        w_spend = pub["wtime"] - callback["wtime"]
        if w_spend > 2*1000000000:  # 2 sec
            pdata["wrong"] = "w_spend>2 sec, cb tid:{} {} {}, pub tid:{} {} {}".format(callback["tid"], callback["thread"], callback["wtime"], pub["tid"], pub["thread"], pub["wtime"])
            continue
        idle_spend = call_pub_time - u_spend - s_spend - w_spend    
        u_percent, s_percent, w_percent, idle_percent = [round(x*1.0/call_pub_time,2) for x in (u_spend,s_spend,w_spend,idle_spend)]
        pdata["use_time"] += call_pub_time
        pdata["path"].append({"type": "call_pub", "node": callback["node"], "use_time": call_pub_time})
        pdata["path"].append({"type": "call_pub_cpu", "node": callback["node"], "u_spend": u_spend, "u_percent": u_percent, "s_spend": s_spend, "s_percent": s_percent, "w_spend": w_spend, "w_percent": w_percent, "idle_spend": idle_spend, "idle_percent": idle_percent})

        ''' add by liyl 20220607 '''
        end=None
        if node_config[pub['node']].get('man_end', '') != '':
            end_tag_name = node_config[pub['node']].get('man_end')
            if beg:
                # this not happen in bus250
                if beg['ident'] in all_man_tag_end.get(end_tag_name,[]):
                    end = all_man_tag_end[end_tag_name][beg['ident']]
                else:
                    print('no end match with beg')
            elif callback['uuid'] in all_man_tag_end.get(end_tag_name,[]):
                end=all_man_tag_end[end_tag_name][callback['uuid']]
        
        if beg or end:  ## at least have one tag
            if not beg:
                beg = callback
            if not end:
                end = pub
            beg_end_time = end["stamp"] - beg["stamp"]
            u_spend = end["utime"] - beg["utime"]
            s_spend = end["stime"] - beg["stime"]
            w_spend = end["wtime"] - beg["wtime"]
            idle_spend = beg_end_time - u_spend - s_spend - w_spend    
            u_percent, s_percent, w_percent, idle_percent = [round(x*1.0/beg_end_time,2) for x in (u_spend,s_spend,w_spend,idle_spend)]
            pdata["path"].append({"type": "beg_end", "node": pub["node"], "use_time": beg_end_time})
            pdata["path"].append({"type": "beg_end_cpu", "node": pub["node"], "u_spend": u_spend, "u_percent": u_percent, "s_spend": s_spend, "s_percent": s_percent, "w_spend": w_spend, "w_percent": w_percent, "idle_spend": idle_spend, "idle_percent": idle_percent})

        analyze_outside_node(callback, pdata, record)

@get_time_used
def analyze_logs():
    global last_timestamp

    result = {}
    target = "/chassis/command"
    target_handle_complate = dict()
    # target = "/topic2"

    if target not in all_sub_msg:
        #all_sub_msg.clear()
        #all_pub_msg.clear()
        last_timestamp += 1*1000000000
        return result

    for uuid in all_sub_msg[target]:
        pub = all_sub_msg[target][uuid]

        record = []
        
        data = {}
        data["use_time"] = 0
        data["path"] = []
        data["split_path"] = []
        # set_car_info(data)  no read used
        record.append(data)

        analyze_outside_node(pub, data, record)
    
        for data in record:
            if data.get("wrong", False) != False:
                #print(data["wrong"])
                continue

            data["split_path_str"] = "_".join(data["split_path"])

            if data["split_path_str"] not in result:
                result[data["split_path_str"]] = []
            result[data["split_path_str"]].append(data)

            if uuid not in target_handle_complate:
                target_handle_complate[uuid] = 1
            else:
                target_handle_complate[uuid] += 1

            if last_timestamp < pub["stamp"] - data['use_time'] - 1*1000000000:  #mod by liyl 20220414 delay 1 sec for test:
                last_timestamp = pub["stamp"] - data['use_time'] - 1*1000000000

    ''' del by liyl because repeat 
    for split_path_str in result:
        result[split_path_str].sort(key=lambda s: s["use_time"], reverse=False)
        #print(len(result[split_path_str]))
    '''

    match_once_num = 0
    for uuid_time, match_num in target_handle_complate.items():
        if match_num == 2:
            del all_sub_msg[target][uuid_time]
        else:
            match_once_num += 1
    if g_test_mode:
        print("add by liyl ######### total_command={}, match_one_times={}".format(len(target_handle_complate), match_once_num))

    all_msg_num = 0
    for topic in all_pub_msg:
        tmp_list = {}
        for uuid in all_pub_msg[topic]:
            if all_pub_msg[topic][uuid]["stamp"] > last_timestamp:
                tmp_list[uuid] = all_pub_msg[topic][uuid]
        all_pub_msg[topic] = tmp_list
        all_msg_num += len(all_pub_msg[topic])

    for topic in all_sub_msg:
        tmp_list = {}
        for uuid in all_sub_msg[topic]:
            if all_sub_msg[topic][uuid]["stamp"] > last_timestamp:
                tmp_list[uuid] = all_sub_msg[topic][uuid]
        all_sub_msg[topic] = tmp_list
        all_msg_num += len(all_sub_msg[topic])
    
    for tag in all_man_tag_end:
        tmp_list = {}
        for uuid in all_man_tag_end[tag]:
            if uuid > last_timestamp:
                tmp_list[uuid] = all_pub_msg[topic][uuid]
        all_man_tag_end[tag] = tmp_list

    if all_msg_num > 10000000:
        all_pub_msg.clear()
        all_sub_msg.clear()

    return result


def get_usetime_pt(result, key="use_time"):
    size = len(result)
    size50 = int(size*0.5)
    size90 = int(size*0.9)
    size99 = int(size*0.99)

    if 'percent' in key:
        return result[size50][key], result[size90][key], result[size99][key]
    else:
        return round(result[size50][key]*1.0/1000000,2), round(result[size90][key]*1.0/1000000,2), round(result[size99][key]*1.0/1000000,2)

def handle_cpu_time(split_data, save_data, mtype, node, type):
    split_data[mtype][node].sort(key=lambda s: s[type], reverse=False)
                
    if node not in save_data[mtype]:
        save_data[mtype][node] = {}
    
    save_data[mtype][node][type] = {} 
    (save_data[mtype][node][type]["p50"], save_data[mtype][node][type]["p90"], save_data[mtype][node][type]["p99"]) = get_usetime_pt(split_data[mtype][node], type)

@get_time_used
def save_logs(output_path, results):
    for split_path_str in results:
        result = results[split_path_str]

        save_data = {}
        result.sort(key=lambda s: s["use_time"], reverse=False)
        (save_data["p50"], save_data["p90"], save_data["p99"]) = get_usetime_pt(result)

        #size = len(result)
        #size99 = int(size*0.99)
        #print(result[size99])

        save_data["pub_recv"] = {}
        save_data["recv_call"] = {}
        save_data["call_pub"] = {}
        save_data["call_pub_cpu"] = {}
        save_data["beg_end"] = {}
        save_data["beg_end_cpu"] = {}

        split_data = {}
        split_data["pub_recv"] = {}
        split_data["recv_call"] = {}
        split_data["call_pub"] = {}
        split_data["call_pub_cpu"] = {}
        split_data["beg_end"] = {}
        split_data["beg_end_cpu"] = {}

        for one in result:
            for data in one["path"]:
                if data["node"] not in split_data[data["type"]]:
                    split_data[data["type"]][data["node"]] = []
        
                split_data[data["type"]][data["node"]].append(data)

        for mtype in split_data:
            if mtype not in ("call_pub_cpu", "beg_end_cpu"):
                for node in split_data[mtype]:
                    split_data[mtype][node].sort(key=lambda s: s["use_time"], reverse=False)
                
                    if node not in save_data[mtype]:
                        save_data[mtype][node] = {}
                    (save_data[mtype][node]["p50"], save_data[mtype][node]["p90"], save_data[mtype][node]["p99"]) = get_usetime_pt(split_data[mtype][node])
            else:
                for node in split_data[mtype]:
                    handle_cpu_time(split_data, save_data, mtype, node, "u_spend")
                    handle_cpu_time(split_data, save_data, mtype, node, "u_percent")
                    handle_cpu_time(split_data, save_data, mtype, node, "s_spend")
                    handle_cpu_time(split_data, save_data, mtype, node, "s_percent")
                    handle_cpu_time(split_data, save_data, mtype, node, "w_spend")
                    handle_cpu_time(split_data, save_data, mtype, node, "w_percent")
                    handle_cpu_time(split_data, save_data, mtype, node, "idle_spend")
                    handle_cpu_time(split_data, save_data, mtype, node, "idle_percent")                    

        save_data["path"] = split_path_str
        save_data["count"] = len(result)
        save_data["timestamp"] = int(last_timestamp/1000000)
        set_car_info(save_data)
        #print(json.dumps(save_data, sort_keys=True, indent=4))
        with open(output_path, "a+") as fp:
            fp.write("{0}\n".format(json.dumps(save_data)))

def handle_logs(output_path, input_paths):
    
    load_logs(input_paths)
 
    result = analyze_logs()

    save_logs(output_path, result)

def prepare_input_files():
    global handle_index
    input_paths = []

    # 分片处理模式，不拉取新文件
    if handle_index >= 0:
        files = os.listdir(tmp_dir)
        for file_name in files:
            tmp_file_path = os.path.join(tmp_dir, file_name)
            input_paths.append(tmp_file_path)
        # print('add by liyl handle_index={}, files={}'.format(handle_index, input_paths))
        return input_paths

    files = os.listdir(input_dir)
    if len(files) > 100:
        #add by liyl if files more than 60, >10s 
        bak_dir = os.path.join(work_dir, "ROS_STAT", "bak_{}".format(int(time.time())))
        os.mkdir(bak_dir)
        for file_name in files:
            os.rename(input_dir+'/'+file_name, bak_dir+'/'+file_name)
        # get newtestfile
        files = os.listdir(input_dir)

    for file_name in files:
        file_path = os.path.join(input_dir, file_name)
        tmp_file_path = os.path.join(tmp_dir, file_name)
        
        os.rename(file_path, tmp_file_path)
        input_paths.append(tmp_file_path)

    return input_paths

def clear_input_files(input_paths):
    global handle_index

    if handle_index >= 0:
        return

    for file_path in input_paths:
        os.remove(file_path)

def run_once():
    input_paths=prepare_input_files()
    if input_paths:
        input_paths.sort()
        handle_logs(output_path, input_paths)
        clear_input_files(input_paths)

    if g_test_mode and log_exceptions_dict:
        print('some log seq error, info is {}'.format(log_exceptions_dict))
        log_exceptions_dict.clear()


def run():
    if os.path.exists(input_dir) == False:
        os.makedirs(input_dir)
    if os.path.exists(tmp_dir) == False:
        os.mkdir(tmp_dir)
    if os.path.exists(output_dir) == False:
        os.mkdir(output_dir)

    read_car_info()
    print("开始分析")
    # dxc 读系统信息
    while True:
        start = time.time()
        run_once()
        end = time.time()
        print('run_once used time {}'.format(end-start))
        
        g_topic_hz_handler.pub_topic_hz_once()

        sleep_time = 1 - (end - start)
        if sleep_time > 0.3:
            time.sleep(sleep_time)


class NodeThread(threading.Thread):
    def __init__(self, topic, msg_type, call_back, parent=None):
        threading.Thread.__init__(self)
        rospy.Subscriber(topic, msg_type, call_back)
    def run(self):
        rospy.spin()

def recv_vstatus(ros_msg):
    global g_pilot_mode

    g_vehicle_state = system_pilot_mode_pb2.SYSVehicleState()
    g_vehicle_state.ParseFromString(ros_msg.data)
    
    if g_test_mode and g_pilot_mode != g_vehicle_state.pilot_mode:
        print('autopilot mode changed to {}!'.format(g_vehicle_state.pilot_mode))
    g_pilot_mode = g_vehicle_state.pilot_mode

class Autopilot:
    def __init__(self):
        rospy.init_node('log_reslove')
        self.veh_state_thread = NodeThread("/system_master/SysVehicleState", BinaryData, recv_vstatus)
    def startThreads(self):
        self.veh_state_thread.start()


if __name__ == '__main__':
    autopilot_thread = Autopilot()
    autopilot_thread.startThreads()
    g_topic_hz_handler = TopicHZ()
    
    run()
