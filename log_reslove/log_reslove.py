#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
import json
import os
import time
import datetime
import threading
import time
import copy
import sys
import json
import os
import copy
import time
import datetime

from config import node_config
import subprocess

import threading

###### ros module
import rospy
import rostopic
import rosgraph
import roslaunch
import rosnode
import rosservice
from std_msgs.msg import String, UInt8, Int32
from rospy import init_node, Subscriber, Publisher
from rospy import rostime

###### mogo
#import proto
from proto import *
from autopilot_msgs.msg import BinaryData

g_vstate_brake_pre    = -1
g_vstate_throttle_pre = -1
g_vstate_brake        = -1
g_vstate_throttle     = -1
g_longitude_driving_mode = -1
g_longitude_driving_mode_pre = -1
g_brake_secs         = 0
g_pilot_mode         = 0
g_pilot_mode_pre     = 0

work_dir = "/home/mogo/data/log"
output_dir = os.path.join(work_dir, "ROS_STAT_RESULT")
output_topic_hz_path = os.path.join(output_dir, "topic_hz")
input_dir = os.path.join(work_dir, "ROS_STAT" ,"EXPORT")
tmp_dir = os.path.join(work_dir, "ROS_STAT_TMP")
output_path = os.path.join(output_dir, "topic_stat")


topic_dict = {}
handle_rate = 1     # 日志过大时切分处理
handle_index = -1
last_timestamp = 0  # 清理已处理过的msg
all_pub_msg = {}
all_sub_msg = {}
node_callback_history = {}

car_info = {}
log_cache_list = []

set_msg_log_pub_info = 0
set_msg_log_pub_error = 0
set_topic_hz_pub = 0
set_log_cache_msg_pub = 0



def listToJson(lst):
    import json
    jsonList = []
    for i in range(len(lst)):
        jsonList.append(i)
    str_json = json.dumps(jsonList)  # json转为string
    return str_json

def buildTopicLogMsg(topic_dict):
    print(topic_dict)
    try:
        log_pub_msg = common_log_reslove.PubLogInfo()
        log_pub_msg.header.seq         = 1
        log_pub_msg.header.stamp.sec   = rostime.Time.now().secs
        log_pub_msg.header.stamp.nsec  = rostime.Time.now().nsecs
        log_pub_msg.header.frame_id    = "log_reslove_frame_id"
        log_pub_msg.header.module_name = "log_reslove"
        log_pub_msg.start_stamp = 0
        log_pub_msg.end_stamp = 0
        for k,v in topic_dict.items():
            start_time = topic_dict[k]['start_time']
            end_time = topic_dict[k]['end_time']
            v["num"] = v["num"]/(end_time-start_time)
            print("time diff is {0}".format((topic_dict[k]['end_time']-topic_dict[k]['start_time'])))
            topic_hz = log_pub_msg.topic_hz.add()
            topic_hz.name = k
            print("the topic dist is {0}".format(topic_dict[k]["dst"]))
            topic_hz.hz = (int)(v["num"]/len(topic_dict[k]["dst"]))
    except Exception as e:
        pass
    return log_pub_msg


def get_topic_hz():
    global topic_dict
    global set_topic_hz_pub
    #print(len(topic_dict))
    topic_dict_copy = copy.deepcopy(topic_dict)
    topic_dict.clear()
    log_pub_msg = buildTopicLogMsg(topic_dict_copy)
    #topic_dict_copy_str = json.dumps(topic_dict_copy)
    #log_pub_msg = buildLogMsg(topic_dict_copy_str)
    log_pub_msg_str = log_pub_msg.SerializeToString()
    topic_hz_msg = BinaryData()

    topic_hz_msg.header.seq         = 1
    topic_hz_msg.header.stamp.secs   = rostime.Time.now().secs
    topic_hz_msg.header.stamp.nsecs  = rostime.Time.now().nsecs
    topic_hz_msg.header.frame_id    = "log_reslove_frame_id"
    topic_hz_msg.name = "log_reslove"
    topic_hz_msg.size = len(log_pub_msg_str)
    topic_hz_msg.data = log_pub_msg_str
    set_topic_hz_pub.publish(topic_hz_msg)

    #for test parse
    test_topic_hz = common_log_reslove.PubLogInfo()
    test_topic_hz.ParseFromString(topic_hz_msg.data)
    for one_topic_hz in test_topic_hz.topic_hz:
        print(one_topic_hz.name)
        print(one_topic_hz.hz)

def anlyzeLogCache():
    global log_cache_list
    global topic_dict
    if len(log_cache_list)<=0:
        return False
    #topic_dict['start_time'] = log_cache_list[0]["stamp"]/1000000000
    #topic_dict['end_time'] = log_cache_list[-1]["stamp"]/1000000000
    for one in log_cache_list:
        try:
            if topic_dict.get(one["topic"]) == None:
                topic_dict[one["topic"]]={}
                topic_dict[one["topic"]]["num"] = 1
                topic_dict[one["topic"]]["start_time"] = 999999999999
                topic_dict[one["topic"]]["end_time"] = 0
                topic_dict[one["topic"]]["dst"] = {}
                topic_dict[one["topic"]]["dst"][one["link"]["dst"]] = 1
            else:
                if topic_dict[one["topic"]]["dst"][one["link"]["dst"]] == None:
                    continue

                topic_dict[one["topic"]]["num"] = topic_dict[one["topic"]]["num"] + 1
            
            if topic_dict.get(one["topic"]) != None: 
                if one["stamp"]/1000000000 < topic_dict[one["topic"]]["start_time"]:
                    topic_dict[one["topic"]]["start_time"] = one["stamp"]/1000000000
                if one["stamp"]/1000000000 > topic_dict[one["topic"]]["end_time"]:
                    topic_dict[one["topic"]]["end_time"] = one["stamp"]/1000000000


        except Exception as e:
            pass
    log_cache_list = []
    return True

class topicThread (threading.Thread):
    def __init__(self, times):
        global set_topic_hz_pub
        threading.Thread.__init__(self)
        self.times = times
        set_topic_hz_pub  = Publisher('/autopilot_info/internal/report_topic_hz', BinaryData, queue_size=10)

    def run(self):
        while True:
            time.sleep(self.times)
            if anlyzeLogCache()==True:
                get_topic_hz()

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
        pass

    try:
        with open("/home/mogo/data/vehicle_monitor/vehicle_config.txt") as fp:
            contents = fp.read().split("\n")

        plate = contents[0].split(":")[-1]
        plate = plate.strip().strip("\"")

        brand = contents[1].split(":")[-1]
        brand = brand.strip().strip("\"")

        car_info["carplate"] = plate
        car_info["cartype"] = brand
    except Exception as e:
        pass

def push_log_cache(one):
    global log_cache_list
    log_cache_list.append(one)

def update_one_log(one):
    global topic_dict
    global g_pilot_mode
    global log_cache_list
    global auto_now_time

    #log cache
    #if len(log_cache_list)<10000 and one["type"] == 0:
    #    log_cache_list.append(one)
    #else:
    #    if len(log_cache_list)>10000 and one["type"] == 0:
    #        log_cache_list.pop(0)
    #        log_cache_list.append(one)

            
    # 0是pub记录
    if one["type"] == 0:
        push_log_cache(one)
        #push topic to list
        #try:
        #    if topic_dict.get(one["topic"]) == None:
        #        topic_dict[one["topic"]] = 1
        #    else:
        #        topic_dict[one["topic"]] = topic_dict[one["topic"]]+1
        #except Exception as e:
        #    pass

        if one["node"] not in node_config:
            return

        if one["topic"] != node_config[one["node"]]["pub"]:
            return

        if g_pilot_mode == 0:
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
                elif one["stamp"] - node_callback_history[sub_topic]["stamp"] > 2000000000 or one["stamp"] < node_callback_history[sub_topic]["stamp"]:
                    #print("mismatch sub")
                    pass
                else:
                    one["use_callback"].append(node_callback_history[sub_topic])

        if one["topic"] not in all_pub_msg:
            all_pub_msg[one["topic"]] = {}
        if one["uuid"] in all_pub_msg[one["topic"]]:
            #print("uuid exist")
            one["uuid_wrong"] = True
        #放到all_pub里面
        all_pub_msg[one["topic"]][one["uuid"]] = one
    # 1是callback记录
    elif one["type"] == 1:
        if one["node"] not in node_config:
            return

        if g_pilot_mode == 0:
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
    else:
        return


def load_one_log(path):
    global handle_index
    lines = []
    try:
        with open(path) as fp:
            contents = fp.read()
            #print(contents)
            lines = contents.split("\n")
    except Exception as e:
        print("receive error")
        pass
    #print("lines len is {0}".format(len(lines)))
    #print("handle_index is {0}".format(handle_index))
    # TODO 切片模式下，不要读所有内容
    #if handle_index >= 0:
    #    size = len(lines)
    #    cut_size = int(size*handle_rate)
    #    start = cut_size * handle_index
    #    end = start + cut_size
    #    if end > size:
    #        end = size
    #    lines = lines[start:end]
    #print("now lines len is {0}".format(len(lines)))

    for line in lines:
        #print(line)
        start = line.find(":", 0, 128)
        if start == -1:
            continue

        start += 1
        if len(line) < start+10:
            continue

        if line[start:start+10] != " #key-log#":
            continue

        start += 10
    
        try:
            one = json.loads(line[start:])
            #print("log is ")
            #print(one)
            update_one_log(one)
        except Exception as e:
        #    print("update log failed {0}".format(line[start:]))
            continue

def load_logs(input_paths):
    global handle_index
    global handle_rate

    #if handle_index == -1:
    #    max_size = 0
    #    for path in input_paths:
    #        stat = os.stat(path)
    #        if max_size <  stat.st_size:
    #            max_size = stat.st_size

    #    if max_size > 5000000:
    #        handle_rate = 5000000/max_size
    #        handle_index = 0

    for path in input_paths:
        load_one_log(path)

    # 分片处理流程
    #if handle_index >= 0:
        # 如果处理完了，恢复全量处理
    #    if handle_index * handle_rate > 0.99:
    #        handle_index = -1
    #        handle_rate = 1
    #    else:
    #        handle_index += 1

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

    use_time = round(float(callback["recv_stamp"] - pub["stamp"])/1000000, 2)
    wait_time = round(float(callback["stamp"] - callback["recv_stamp"])/1000000, 2)
    if use_time + wait_time > 2000:
        #print("pub-callback use time {0}".format(use_time))
        data["wrong"] = ">2000"
        return

    data["use_time"] += use_time + wait_time
    data["path"].append({"type":"pub_recv", "node":callback["node"], "use_time":use_time})
    data["path"].append({"type":"recv_call", "node":callback["node"], "use_time":wait_time})

    analyze_inside_node(pub, data, record)

def analyze_inside_node(pub, data, record):
    if pub.get("no_callback", False) != False:
        return

    if "use_callback" not in pub or len(pub["use_callback"]) == 0:
        #print("no use_callback")
        data["wrong"] = "can't find callback"
        return

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

        simple_path = False
        if pub.get("uuid_wrong", False) == True or callback.get("uuid_wrong", False) == True:
            #print("uuid wrong 3")
            #print(pub)
            #print(callback)
            pdata["wrong"] = "uuid wrong"
            continue

        use_time = round(float(pub["stamp"] - callback["stamp"])/1000000, 2)
        if use_time > 2000:
            #print("callback-pub use time {0}".format(use_time))
            pdata["wrong"] = ">2000"
            continue

        u_spend = round(float(pub["utime"] - callback["utime"])/1000000, 2)
        u_percent = round(float(u_spend / use_time), 2)
        s_spend = round(float(pub["stime"] - callback["stime"])/1000000, 2)
        s_percent = round(float(s_spend / use_time), 2)
        w_spend = round(float(pub["wtime"] - callback["wtime"])/1000000, 2)
        if w_spend > 2000:
            pdata["wrong"] = "w_spend>2000, cb tid:{} {} {}, pub tid:{} {} {}".format(callback["tid"], callback["thread"], callback["wtime"], pub["tid"], pub["thread"], pub["wtime"])
            continue
        w_percent = round(float(w_spend / use_time), 2)
        idle_spend = round(float(use_time - u_spend - s_spend - w_spend), 2)
        idle_percent = round(float(idle_spend / use_time), 2)

        pdata["use_time"] += use_time
        pdata["path"].append({"type": "call_pub", "node": callback["node"], "use_time": use_time})
        pdata["path"].append({"type": "call_pub_cpu", "node": callback["node"], "u_spend": u_spend, "u_percent": u_percent, "s_spend": s_spend, "s_percent": s_percent, "w_spend": w_spend, "w_percent": w_percent, "idle_spend": idle_spend, "idle_percent": idle_percent})
        analyze_outside_node(callback, pdata, record)


def analyze_logs():
    global last_timestamp

    result = {}
    target = "/chassis/command"
    # target = "/topic2"

    if target not in all_sub_msg:
        all_sub_msg.clear()
        all_pub_msg.clear()
        return result

    for uuid in all_sub_msg[target]:
        pub = all_sub_msg[target][uuid]

        record = []
        
        data = {}
        data["use_time"] = 0
        data["path"] = []
        data["split_path"] = []
        set_car_info(data)
        record.append(data)

        analyze_outside_node(pub, data, record)
    
        for data in record:
            if data.get("wrong", False) != False:
                #print(data["wrong"])
                continue

            data["use_time"] = round(data["use_time"], 2)
            data["split_path_str"] = "_".join(data["split_path"])

            if data["split_path_str"] not in result:
                result[data["split_path_str"]] = []
            result[data["split_path_str"]].append(data)

            if last_timestamp < pub["stamp"]:
                last_timestamp = pub["stamp"]

    for split_path_str in result:
        result[split_path_str].sort(key=lambda s: s["use_time"], reverse=False)
        #print(len(result[split_path_str]))

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

    if all_msg_num > 1000000:
        all_pub_msg.clear()
        all_sub_msg.clear()

    return result

def get_usetime_pt(result, key="use_time"):
    size = len(result)
    size50 = int(size*0.5)
    size90 = int(size*0.9)
    size99 = int(size*0.99)

    return result[size50][key], result[size90][key], result[size99][key]

def handle_cpu_time(split_data, save_data, mtype, node, type):
    split_data[mtype][node].sort(key=lambda s: s[type], reverse=False)
                
    if node not in save_data[mtype]:
        save_data[mtype][node] = {}
    
    save_data[mtype][node][type] = {} 
    (save_data[mtype][node][type]["p50"], save_data[mtype][node][type]["p90"], save_data[mtype][node][type]["p99"]) = get_usetime_pt(split_data[mtype][node], type)

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

        split_data = {}
        split_data["pub_recv"] = {}
        split_data["recv_call"] = {}
        split_data["call_pub"] = {}
        split_data["call_pub_cpu"] = {}

        for one in result:
            for data in one["path"]:
                if data["node"] not in split_data[data["type"]]:
                    split_data[data["type"]][data["node"]] = []
        
                split_data[data["type"]][data["node"]].append(data)

        for mtype in split_data:
            if mtype != "call_pub_cpu":
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
    start = time.time()
    load_logs(input_paths)
    end = time.time()
    print("load log use time {0}".format(end-start))

    start = time.time()
    result = analyze_logs()
    end = time.time()
    print("analyze log use time {0}".format(end-start))

    start = time.time()
    save_logs(output_path, result)
    end = time.time()
    print("save log use time {0}".format(end-start))

def prepare_input_files():
    global handle_index

    # 分片处理模式，不拉取新文件
    if handle_index >= 0:
        input_paths = []
        files = os.listdir(tmp_dir)
        for file_name in files:
            tmp_file_path = os.path.join(tmp_dir, file_name)
            input_paths.append(tmp_file_path)

        return input_paths

    input_paths = []
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
    input_paths = prepare_input_files()
    handle_logs(output_path, input_paths)
    clear_input_files(input_paths)

def run():
    if os.path.exists(tmp_dir) == False:
        os.mkdir(tmp_dir)
    if os.path.exists(output_dir) == False:
        os.mkdir(output_dir)

    read_car_info()
    #print("开始分析")
    # dxc 读系统信息
    while True:
        start = time.time()
        run_once()
        end = time.time()

        sleep_time = 5 - (end - start)
        if sleep_time > 0.3:
            time.sleep(sleep_time)


auto_now_time = 0
class NodeThread(threading.Thread):
    def __init__(self, topic, msg_type, call_back, parent=None):
        threading.Thread.__init__(self)
        rospy.Subscriber(topic, msg_type, call_back)
    def run(self):
        rospy.spin()


def recv_vstatus(ros_msg):
    #global  g_vehicle_state
    global auto_now_time
    auto_now_time = ros_msg.header.stamp.secs*1000 + ros_msg.header.stamp.nsecs/1000
    #print(now_time)
    g_vehicle_state = common_vehicle_state.VehicleState()
    g_vehicle_state.ParseFromString(ros_msg.data)
    global g_vstate_brake
    global g_vstate_throttle
    global g_longitude_driving_mode
    global g_pilot_mode
    g_vstate_brake    = g_vehicle_state.brake
    g_vstate_throttle = g_vehicle_state.throttle
    g_longitude_driving_mode = g_vehicle_state.longitude_driving_mode
    g_pilot_mode = g_vehicle_state.pilot_mode

class Autopilot:
    def __init__(self):
        #super(Autopilot, self).__init__()
        rospy.init_node('log_reslove')
        self.startThreads()
    def startThreads(self):
        self.veh_state_thread = NodeThread("/chassis/vehicle_state", BinaryData, recv_vstatus)
        self.veh_state_thread.start()


def PrepareMsgLogPath():
    input_paths = []
    files = os.listdir("/home/mogo/data/log/msg_log/")
    for file_name in files:
        file_path = os.path.join("/home/mogo/data/log/msg_log/", file_name)
        tmp_file_path = os.path.join("/home/mogo/data/log/msg_log_temp/", file_name)

        os.rename(file_path, tmp_file_path)
        input_paths.append(tmp_file_path)
    return input_paths

def LoadMsglogs(input_paths):
    for path in input_paths:
        LoadOneMsgLog(path)

def buildOneLogMsg(one_log_dict):
    #common_mogo_report_msg MogoReportMessage
    mogo_report_msg = common_mogo_report_msg.MogoReportMessage()
    try:
        mogo_report_msg.timestamp.sec = one_log_dict["timestamp"]["sec"]
        mogo_report_msg.timestamp.nsec = one_log_dict["timestamp"]["nsec"]
        mogo_report_msg.src = one_log_dict["src"]
        mogo_report_msg.level = one_log_dict["level"]
        mogo_report_msg.msg = one_log_dict["msg"]
        mogo_report_msg.code = one_log_dict["code"]
        if one_log_dict["level"] == "error":
            for result in one_log_dict["result"]:
                mogo_report_msg.result.append(result)
            for action in one_log_dict["actions"]:
                mogo_report_msg.actions.append(action)
        else:
            mogo_report_msg.result.append("")
            mogo_report_msg.actions.append("")
        #temp_action =  mogo_report_msg.action.add()
        #temp_action = action
    except Exception as e:
        pass
    return mogo_report_msg


def LoadOneMsgLog(path):
    with open(path) as fp:
        contents = fp.read()
        lines = contents.split("\n")
    for line in lines:
        one_log_dict = {}
        #print("line json is ")
        #print(line)
        try:
            one_log_dict = json.loads(line)
        except Exception as e:
            continue
        #convert json to protobuf
        log_pub_msg = buildOneLogMsg(one_log_dict)
        log_pub_msg_str = log_pub_msg.SerializeToString()
        binary_log_msg = BinaryData()

        binary_log_msg.header.seq         = 1
        binary_log_msg.header.stamp.secs   = rostime.Time.now().secs
        binary_log_msg.header.stamp.nsecs  = rostime.Time.now().nsecs
        binary_log_msg.header.frame_id    = "log_reslove_frame_id"
        binary_log_msg.name = "log_reslove"
        binary_log_msg.size = len(log_pub_msg_str)
        binary_log_msg.data = log_pub_msg_str
        print(log_pub_msg_str)
        if one_log_dict["level"] == "info":
            set_msg_log_pub_info.publish(binary_log_msg)
        if one_log_dict["level"] == "error":
            set_msg_log_pub_error.publish(binary_log_msg)

        mogo_report_msg_test = common_mogo_report_msg.MogoReportMessage()
        mogo_report_msg_test.ParseFromString(binary_log_msg.data)
        for one_msg in mogo_report_msg_test.actions:
            print(one_msg)
        for one_msg in mogo_report_msg_test.result:
            print(one_msg)
        time.sleep(1)


def UpdateMsgTopic():
    while(True):
        input_paths=PrepareMsgLogPath()
        if len(input_paths)>0:
             LoadMsglogs(input_paths)
        else:
            time.sleep(1)
        #os.system("rm -f /home/mogo/data/log/msg_log_temp/*")


class MsgLogThread (threading.Thread):
    def __init__(self):
        global set_msg_log_pub_info
        global set_msg_log_pub_error
        threading.Thread.__init__(self)
        set_msg_log_pub_info  = Publisher('/autopilot_info/internal/report_msg_info', BinaryData, queue_size=10)
        set_msg_log_pub_error = Publisher('/autopilot_info/internal/report_msg_error', BinaryData, queue_size=10)

    def run(self):
        UpdateMsgTopic()


def main():
    autopilot_thread = Autopilot()
    
    topic_thread = topicThread(5)
    topic_thread.start()
    
    msg_log_thread = MsgLogThread()
    msg_log_thread.start()
    #log_msg_thread = logMsgThread(5)
    #log_msg_thread.start()

    run()

main()
