#!/usr/bin/python3
import sys
import json
import os
import copy
import time
from config import node_config

#config_path = "/root/config.json"
work_dir = "/home/mogo/data/log"
#work_dir = "/Users/dengwrex/Desktop/mogo_ros/keylog_parser"
input_dir = os.path.join(work_dir, "ROS_STAT", "EXPORT")
tmp_dir = os.path.join(work_dir, "ROS_STAT_TMP")
output_dir = os.path.join(work_dir, "ROS_STAT_RESULT")
output_path = os.path.join(output_dir, "topic_stat")

'''
node_config = {}
node_config["/DongFeng_E70_can_adapter"] = {}
node_config["/DongFeng_E70_can_adapter"]["sub"] = ["/chassis/command"]
node_config["/DongFeng_E70_can_adapter"]["pub"] = ""

#node_config["/jinlv_can_adapter"] = {}
#node_config["/jinlv_can_adapter"]["sub"] = ["/chassis/command"]
#node_config["/jinlv_can_adapter"]["pub"] = ""

node_config["/controller"] = {}
node_config["/controller"]["sub"] = ["/planning/trajectory"]
node_config["/controller"]["pub"] = "/chassis/command"

node_config["/local_planning"] = {}
node_config["/local_planning"]["sub"] = ["/perception/fusion/obstacles"]
node_config["/local_planning"]["pub"] = "/planning/trajectory"

node_config["/perception/fusion/perception_fusion2"] = {}
node_config["/perception/fusion/perception_fusion2"]["sub"] = ["/perception/lidar/lidar_obstacle", "/perception/camera/camera_obstacle"]
node_config["/perception/fusion/perception_fusion2"]["pub"] = "/perception/fusion/obstacles"

#node_config["/perception/fusion/perception_fusion"] = {}
#node_config["/perception/fusion/perception_fusion"]["sub"] = ["/perception/lidar/lidar_obstacle_cluster", "/perception/camera/camera_obstacle"]
#node_config["/perception/fusion/perception_fusion"]["pub"] = "/perception/fusion/obstacles"

node_config["/perception/lidar/rs_perception_node"] = {}
node_config["/perception/lidar/rs_perception_node"]["sub"] = ["/sensor/lidar/middle/point_cloud"]
node_config["/perception/lidar/rs_perception_node"]["pub"] = "/perception/lidar/lidar_obstacle"

#node_config["/perception/lidar/perception_lidar"] = {}
#node_config["/perception/lidar/perception_lidar"]["sub"] = ["/sensor/lidar/front_left/point_clound", "/sensor/lidar/front_right/point_cloud"]
#node_config["/perception/lidar/perception_lidar"]["pub"] = "/perception/lidar/lidar_obstacle"

node_config["/sensor/lidar/robosense/drivers_robosense_node"] = {}
node_config["/sensor/lidar/robosense/drivers_robosense_node"]["sub"] = []
node_config["/sensor/lidar/robosense/drivers_robosense_node"]["pub"] = "/sensor/lidar/middle/point_cloud"

node_config["/sensor/lidar/robosense/drivers_robosense_node"] = {}
node_config["/sensor/lidar/robosense/drivers_robosense_node"]["sub"] = []
node_config["/sensor/lidar/robosense/drivers_robosense_node"]["pub"] = "/sensor/lidar/middle/point_cloud"

#node_config["/sensor/lidar/c32/front_left/c32_left_decoder"] = {}
#node_config["/sensor/lidar/c32/front_left/c32_left_decoder"]["sub"] = []
#node_config["/sensor/lidar/c32/front_left/c32_left_decoder"]["pub"] = "/sensor/lidar/front_left/point_clound"

#node_config["/sensor/lidar/c32/front_right/c32_right_decoder"] = {}
#node_config["/sensor/lidar/c32/front_right/c32_right_decoder"]["sub"] = []
#node_config["/sensor/lidar/c32/front_right/c32_right_decoder"]["pub"] = "/sensor/lidar/front_right/point_clound"

node_config["/trt_yolov5"] = {}
node_config["/trt_yolov5"]["sub"] = ["/sensor/camera/sensing/image_raw_60"]
node_config["/trt_yolov5"]["pub"] = "/perception/camera/camera_obstacle"

node_config["/sensor/camera/sensing60/drivers_camera_sensing60"] = {}
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["sub"] = []
node_config["/sensor/camera/sensing60/drivers_camera_sensing60"]["pub"] = "/sensor/camera/sensing/image_raw_60"
'''

handle_rate = 1     # 日志过大时切分处理
handle_index = -1
last_timestamp = 0  # 清理已处理过的msg
all_pub_msg = {}
all_sub_msg = {}
node_callback_history = {}

car_info = {}


def load_config_info():
    if os.path.exists(tmp_dir) == False:
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            node_config = json.load(f)
    except Exception as e:
        return False
    print(node_config)
    for kv in node_config.items():
       print(kv)
    return True;


def set_car_info(data):
    data["code_version"] = car_info.get("code_version", "")
    data["carplate"] = car_info.get("carplate", "")
    data["cartype"] = car_info.get("cartype", "")

def read_car_info():
    try:
        with open("project_commit.txt") as fp:
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
        return False
    return True

def update_one_log(one):
    if one["node"] not in node_config:
        #if one["node"] == "/DongFeng_E70_can_adapter":
        #print("node not in node_config ")
        #    print(one["node"])
        return

    # 0是pub记录
    if one["type"] == 0:
        if one["topic"] != node_config[one["node"]]["pub"]:
            return

        if one["link"]["dst"] not in node_config:
            return

        one["uuid"] = one["header_stamp"]
        if one["uuid"] == 0:
            one["uuid"] = one["feature"]

        one["use_callback"] = []
        #指定节点下面订阅字典
        if len(node_config[one["node"]]["sub"]) == 0:
            one["no_callback"] = True
        for sub_topic in node_config[one["node"]]["sub"]:
            if sub_topic not in node_callback_history: #如果不在history里面
                if sub_topic != "":
                    #print("can not find sub {0}".format(sub_topic))
                    pass
            else:
                if node_callback_history[sub_topic]["thread"] != one["thread"]:
                    print("pub/sub in different thread")
                    pass
                elif one["stamp"] - node_callback_history[sub_topic]["stamp"] > 2000000000 or one["stamp"] < node_callback_history[sub_topic]["stamp"]:
                    print("mismatch sub")
                    pass
                else:
                    one["use_callback"].append(node_callback_history[sub_topic])

        if one["topic"] not in all_pub_msg:
            all_pub_msg[one["topic"]] = {}
        if one["uuid"] in all_pub_msg[one["topic"]]:
            #print("uuid exist")
            one["uuid_wrong"] = True
        all_pub_msg[one["topic"]][one["uuid"]] = one
    # 1是callback记录
    elif one["type"] == 1:
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
    with open(path) as fp:
        contents = fp.read()
        lines = contents.split("\n")

    # TODO 切片模式下，不要读所有内容
    if handle_index >= 0:
        size = len(lines)
        cut_size = int(size*handle_rate)
        start = cut_size * handle_index
        end = start + cut_size
        if end > size:
            end = size
        lines = lines[start:end]

    for line in lines:
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
            update_one_log(one)
        except Exception as e:
            #print("update log failed {0}".format(line[start:]))
            continue

def load_logs(input_paths):
    global handle_index
    global handle_rate

    if handle_index == -1:
        max_size = 0
        for path in input_paths:
            stat = os.stat(path)
            if max_size <  stat.st_size:
                max_size = stat.st_size

        if max_size > 5000000:
            handle_rate = 5000000/max_size
            handle_index = 0

    for path in input_paths:
        load_one_log(path)

    # 分片处理流程
    if handle_index >= 0:
        # 如果处理完了，恢复全量处理
        if handle_index * handle_rate > 0.99:
            handle_index = -1
            handle_rate = 1
        else:
            handle_index += 1

def analyze_outside_node(callback, data, record):
    if callback["topic"] not in all_pub_msg:
        print("no topic")
        data["wrong"] = "on topic in pub"
        return

    if callback.get("uuid_wrong", False) == True:
        print("uuid wrong 1")
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
    if use_time<0 or wait_time<0:
        print("callbckrecv_stamp {0}".format(callback["recv_stamp"]))
        print("pubstamp {0} ".format(pub["stamp"]/1000000))
        print("callbackstamp {0}".format(callback["stamp"]))
    if use_time + wait_time > 2000:
        print("pub-callback use time {0}".format(use_time))
        data["wrong"] = ">2000"
        return

    data["use_time"] += use_time + wait_time
    data["path"].append({"type":"pub_recv", "node":callback["node"], "use_time":use_time})
    data["path"].append({"type":"recv_call", "node":callback["node"], "use_time":wait_time})

    analyze_inside_node(pub, data, record)

def analyze_inside_node(pub, data, record):
    if pub.get("no_callback", False) != False:
        #胜利收工
        return

    if "use_callback" not in pub or len(pub["use_callback"]) == 0:
        print("no use_callback")
        data["wrong"] = "can't find callback"
        #return

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
            print("uuid wrong 3")
            #print(pub)
            #print(callback)
            pdata["wrong"] = "uuid wrong"
            continue

        use_time = round(float(pub["stamp"] - callback["stamp"])/1000000, 2)
        if use_time > 2000:
            print("callback-pub use time {0}".format(use_time))
            pdata["wrong"] = ">2000"
            continue

        pdata["use_time"] += use_time
        pdata["path"].append({"type":"call_pub", "node":callback["node"], "use_time":use_time})
        analyze_outside_node(callback, pdata, record)


def analyze_logs():
    global last_timestamp

    result = {}
    target = "/chassis/command"

    '''
    print("all_sub_msg")
    for topic in all_sub_msg:
        print("{0}  {1}".format(topic, len(all_sub_msg[topic])))

    print("all_pub_msg")
    for topic in all_pub_msg:
        print("{0}  {1}".format(topic, len(all_pub_msg[topic])))
    '''

    #print("all sub message is {0}".format(all_sub_msg))

    if target not in all_sub_msg:
        all_sub_msg[target] = {}
    else:
        print("target is {0}".format(target))

    #print("all_sub_msg[target] is {0}".format(all_sub_msg[target]))
    # 我们从target逆向找的，所以有比target小的信息都可以在本轮完成后丢弃
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
                print(data["wrong"])
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

    # 清理不需要的数据
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
        # TODO 优雅一点，按时间排个序把老的删了，新的留下
        all_pub_msg.clear()
        all_sub_msg.clear()
        print("too many msg, clear all")

    return result

def get_usetime_pt(result):
    size = len(result)
    size50 = int(size*0.5)
    size90 = int(size*0.9)
    size99 = int(size*0.99)

    return result[size50]["use_time"], result[size90]["use_time"], result[size99]["use_time"]

def save_logs(output_path, results):
    # TODO 每秒切一个统计
    for split_path_str in results:
        result = results[split_path_str]

        # 全链路延迟
        save_data = {}
        result.sort(key=lambda s: s["use_time"], reverse=False)
        (save_data["p50"], save_data["p90"], save_data["p99"]) = get_usetime_pt(result)

        #size = len(result)
        #size99 = int(size*0.99)
        #print(result[size99])

        # 各环节分解延迟
        save_data["pub_recv"] = {}
        save_data["recv_call"] = {}
        save_data["call_pub"] = {}

        split_data = {}
        split_data["pub_recv"] = {}
        split_data["recv_call"] = {}
        split_data["call_pub"] = {}

        for one in result:
            for data in one["path"]:
                if data["node"] not in split_data[data["type"]]:
                    split_data[data["type"]][data["node"]] = []
        
                split_data[data["type"]][data["node"]].append(data)

        for mtype in split_data:
            for node in split_data[mtype]:
                split_data[mtype][node].sort(key=lambda s: s["use_time"], reverse=False)
            
                if node not in save_data[mtype]:
                    save_data[mtype][node] = {}
                (save_data[mtype][node]["p50"], save_data[mtype][node]["p90"], save_data[mtype][node]["p99"]) = get_usetime_pt(split_data[mtype][node])

        save_data["path"] = split_path_str
        save_data["count"] = len(result)
        save_data["timestamp"] = int(last_timestamp/1000000)
        set_car_info(save_data)
        #print(json.dumps(save_data, sort_keys=True, indent=4))
        with open(output_path, "a+") as fp:
            fp.write("{0}\n".format(json.dumps(save_data)))

# 处理1000秒记录数据，load耗时10秒，analyze耗时2秒，save耗时0.5秒；内存吃到了800MB，内存有风险
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
    print("result is {0}".format(result))

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


    if read_car_info() == False:
        return;

    #if load_config_info() == False:
    #    return;

    # dxc 读系统信息
    while True:
        start = time.time()
        run_once()
        end = time.time()

        sleep_time = 5 - (end - start)
        if sleep_time > 0.3:
            time.sleep(sleep_time)

def main():
    #return run()
    while True:
        pid = os.fork()
        if pid == 0:
            run()
        else:
            os.waitpid(pid, 0)
            print("child exit, rerun")
            time.sleep(1)

if __name__ == '__main__':
    main()
