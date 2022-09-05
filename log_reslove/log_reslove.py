#!/usr/bin/python3

import os
import time
#import asyncio
import threading
import json
import copy
import datetime
import traceback
from config import node_config

import rospy 
from autopilot_msgs.msg import BinaryData
from proto import system_pilot_mode_pb2


#global param
all_link_node_list = dict()   # k=name, v=node_entry
all_link_topic_list = dict()  # k=name, v={uuid: topic_entry}

g_test_mode = False
g_pilot_mode_list = list()  # [[start1,end1],[start2,end2]]

#constant
class Constants():
    work_dir = "/home/mogo/data/log"
    output_dir = os.path.join(work_dir, "ROS_STAT_RESULT")
    input_dir = os.path.join(work_dir, "ROS_STAT" ,"EXPORT")
    tmp_dir = os.path.join(work_dir, "ROS_STAT_TMP")
    bak_dir = os.path.join(work_dir, "ROS_STAT", '{}'.format(datetime.date.today()))
    output_file = os.path.join(output_dir, "topic_stat")
    g_time_split_threshold = 30   # second
    g_type_of_pub = 0
    g_type_of_sub = 1
    g_type_of_beg = 2
    g_type_of_end = 3
    unit_stamp_sec = 1000000000
    

#utils
def get_time_used(func):
    def wrapper(*args,**kwargs):
        start_time=time.time()
        ret = func(*args,**kwargs)
        end_time=time.time()
        if g_test_mode or 1 < end_time - start_time:
            print('{} used time is {}'.format(func.__name__, end_time-start_time))
        return ret
    return wrapper

"""
0：pub: 一个topic输出
1：sub: 有多个输入（融合）
2：man_beg: 手动埋点开始
3：man_end: 手动埋点结束

1、	同一个node,  pub之前必有sub，每个pub对应的sub取时间最近的
单线程处理节点通过线程id匹配，多线程节点只能按link和时间匹配
时间从小到大，采用稳定匹配算法
（查看camera_2D一个进程写入文件是顺序的，按事件排序即可）
2、	同一个topic，pub与sub之间的uuid是相同的（ident）
多路情况存在多个相同的uuid的pub，需要通过link来去除冗余。 
3、	自动驾驶开始与结束时间的匹配，日志处理需要确定时间范围
4、man_beg 与 man_end 用于补偿pub和sub，
优先判断ident，ident不为0时候，匹配thread_id, 按时间匹配
如果ident为0，是否证明是单线程？
5、beg_end time计算时候，如果beg end都存在，采用beg，end计算
"""

class Node_base(object):
    """
    以节点创建类，将相关属性实例化，用于topic和 tag 的匹配关联
    """
    def __init__(self, name):
        self.name = name
        self.id_list = set()   # thread_id
        # self.thread_id = None  # add by liyl for single thread
        self.sub_topic_list = node_config[name].get('sub', [])   
        self.pub_topic = node_config[name].get('pub', '')
        self.beg_tag = node_config[name].get('man_beg', '')
        self.end_tag = node_config[name].get('man_end', '')
        self.is_start_node = False if self.sub_topic_list else True  
        self.sub_msg_dict = dict()  # { 'thread_id': { k=topic_name: v=sub_topic}}
        self.finish_dict = dict()   # { k=pub_uuid: V=sub_uuid_dict}
        self.beg_msg_dict = dict()  # { k=beg_ident: v=beg_info}
        self.end_msg_dict = dict()  # { k=end_ident: v=end_info}
        self.beg_end_info = dict()  # { k=end_dict: v=beg_ident}
    
    def update_node_info(self, one):
        """
        更新节点信息，topic和tag分别处理
        """
        try:
            if 'topic' in one and one['topic'] in all_link_topic_list:
                
                if 'link' not in one or 'thread' not in one:
                    return
                if one['link'].get('src', 'unknow') not in all_link_node_list or one['link'].get('dst', 'unknow') not in all_link_node_list:
                    return

                if one['topic'] in self.sub_topic_list or one['topic'] == self.pub_topic:
                    # 判断topic链路，防止跨节点的uuid重复
                    topic_uuid = one['ident'] if one.get('ident', 0) else one['header_stamp'] or one['feature']
                    if topic_uuid not in all_link_topic_list[one['topic']]:
                        self.create_topic_info( topic_uuid, one)
                    else:
                        self.update_topic_info( topic_uuid, one)
                else:
                    return
                    
                if one['type'] == Constants.g_type_of_pub:
                    # 该节点发送的 pub消息
                    if one['thread'] in self.sub_msg_dict and self.sub_msg_dict[one['thread']]:
                        self.finish_dict[topic_uuid] = copy.deepcopy(self.sub_msg_dict[one['thread']])
                    elif not self.is_start_node:
                        print('wrong: The [{}] no sub msg callback before!'.format(self.name))
                    
                    if self.beg_tag and self.end_tag:
                        ##TODO don't need handle, but need match topic and tag by time 
                        pass
                    elif self.beg_tag:
                        ## only beg_tag in node, MAP260 need support
                        if topic_uuid in self.beg_msg_dict:
                            self.update_beg_tag_info(topic_uuid, one['topic'], self.beg_msg_dict[topic_uuid])
                        elif one['thread'] in self.beg_msg_dict:
                            # uuid 不匹配 pub topic的ident， 那么用线程进行匹配，单线程只有一个数据
                            self.update_beg_tag_info(topic_uuid, one['topic'], self.beg_msg_dict[one['thread']])
                
                elif one['type'] == Constants.g_type_of_sub:
                    # 该节点接收的 sub消息
                    if one['topic'] in self.sub_topic_list:
                        # 顺序记录sub topic，按thread匹配，只保留最近一次，这样多线程不可以最近匹配
                        if one['thread'] not in self.sub_msg_dict:
                            self.sub_msg_dict[one['thread']] = dict()
                        self.sub_msg_dict[one['thread']][one['topic']] = topic_uuid
                else:
                    print('the type is {} should not in topic msg'.format(one['type']))

            elif 'tag' in one:
                ## 手动埋点消息处理
                if one['type'] == Constants.g_type_of_beg:
                    if one['tag'] != self.beg_tag:
                        return
                    tag_uuid = one['ident'] or one['thread']
                    self.beg_msg_dict[tag_uuid] = one
                elif one['type'] == Constants.g_type_of_end:
                    if one['tag'] != self.end_tag:
                        return
                    tag_uuid = one['ident'] or one['thread']
                    self.end_msg_dict[tag_uuid] = one
                    if self.beg_tag:
                        #TODO add beg and end match handle
                        if tag_uuid in self.beg_msg_dict:
                            # 生成beg end的配对关系
                            self.beg_end_info['tag_uuid']=(self.beg_msg_dict[tag_uuid], self.end_msg_dict[tag_uuid])
                    else:
                        #TODO add only sub match handle
                        pass

        except Exception as e:
            print('update node info error! {}'.format(e))
            print ("exception happend")
            print ('str(Exception):\t', str(Exception))
            print ('str(e):\t', str(e))
            print ('repr(e):\t', repr(e))
            print ('traceback.format_exc():\n%s' % (traceback.format_exc()))  

    def create_topic_info(self, uuid, one):
        """
        创建topic信息，加入到全局列表里，topic信息里包含pub，sub 关联beg，end
        {"type":0,"node":"/controller","topic":"/chassis/command",
        "link":{"src":"/controller","dst":"/jinlv_can_adapter"},
        "thread":547556995424,"ident":1658220898474152816,
        "stamp":1658220898474844432,"recv_stamp":0,
        "utime":431280000000,"stime":120644000000,"wtime":4149215200}
        """
        topic_entity = all_link_topic_list[one['topic']][uuid] = dict()
        topic_entity['uuid'] = uuid  # one['ident'] # header_stamp or feature
        topic_entity['topic'] = one['topic']
        topic_entity['thread'] = one['thread']
        topic_entity['send_node'] = None  # node_entity
        topic_entity['recv_node'] = None  # node_entity
        topic_entity['next_topic'] = None  # topic entity for one pub depend more sub
        topic_entity['finish_flag'] = False  # if True, the topic in finish
        topic_entity['info'] = dict()
        self.update_topic_info(uuid, one)
    
    def update_topic_info(self, uuid, one):
        topic_entity = all_link_topic_list[one['topic']][uuid]
        if one['type'] == Constants.g_type_of_pub:
            if one['node'] in all_link_node_list:
                topic_entity['send_node'] = all_link_node_list[one['node']]
                topic_entity['info']['link'] = one['link']
                topic_entity['info']['pub_stamp'] = one['stamp']
                topic_entity['info']['pub_stime'] = one['stime']
                topic_entity['info']['pub_utime'] = one['utime']
                topic_entity['info']['pub_wtime'] = one['wtime']

        if one['type'] == Constants.g_type_of_sub:
            if one['node'] in all_link_node_list:
                topic_entity['recv_node'] = all_link_node_list[one['node']]
                topic_entity['info']['recv_stamp'] = one['recv_stamp']
                topic_entity['info']['call_stamp'] = one['stamp']
                topic_entity['info']['sub_stime'] = one['stime']
                topic_entity['info']['sub_utime'] = one['utime']
                topic_entity['info']['sub_wtime'] = one['wtime']

        if topic_entity.get('send_node', None) and topic_entity.get('recv_node',None):
            topic_entity['finish_flag'] = True
 
    def update_beg_tag_info(self, uuid, topic_name, one):
        #key-log#{"type":2,"node":"/sensor/camera/sensing60/drivers_camera_sensing60",
        # "tag":"camera_grab","thread":548320079888,"ident":0,"stamp":1656557475569788227,
        # "utime":392164000000,"stime":88036000000,"wtime":134121769824}
        topic_entity = all_link_topic_list[topic_name][uuid]
        topic_entity['beg_info'] = one


class Log_handler():
    """
    整体处理类，从日志加载到数据输出，周期性处理
    """
    def __init__(self) -> None:
        self.car_info = Car_Status()
        self.last_timestamp = time.time() * Constants.unit_stamp_sec
        self.handle_index = -1
        self.test_mode = True
        self.time_split_threshold = Constants.g_time_split_threshold
        self.time_start_value = 0
        self.time_split_value = 0
        self.time_split_end = 0
        self.input_paths = list()
        self.results = dict()
        

    def prepare_input_files(self):
        self.input_paths = list()

        # 分片处理模式，不拉取新文件
        if self.handle_index >= 0:
            files = os.listdir(Constants.tmp_dir)
            for file_name in files:
                tmp_file_path = os.path.join(Constants.tmp_dir, file_name)
                self.input_paths.append(tmp_file_path)
            print('add by liyl handle_index={}'.format(self.handle_index))
            return

        files = os.listdir(Constants.input_dir)
        if not g_test_mode and len(files) > 100:
            #add by liyl if files more than 60, >10s 日志文件过大不处理，放置到备份目录
            bak_dir = os.path.join(Constants.bak_dir, "bak_{}".format(int(time.time())))
            os.mkdir(bak_dir)
            for file_name in files:
                if '.tmp' in file_name:
                    continue
                os.rename(Constants.input_dir+'/'+file_name, bak_dir+'/'+file_name)
            # get newtestfile
            files = os.listdir(Constants.input_dir)

        for file_name in files:
            if '.tmp' in file_name:
                continue
            file_path = os.path.join(Constants.input_dir, file_name)
            tmp_file_path = os.path.join(Constants.tmp_dir, file_name)
            
            os.rename(file_path, tmp_file_path)
            self.input_paths.append(tmp_file_path)
        
        self.input_paths.sort()

    def load_one_log(self, one):

        if one.get('node', 'unknow') in all_link_node_list:
            # node 在解析配置字典里，进行数据更新
            all_link_node_list[one['node']].update_node_info(one)


    ''' handel file one by one '''
    def load_one_log_by_time(self, ros_time_paths, remote_paths):
        global g_pilot_mode_list
  
        if not g_test_mode:
            if not g_pilot_mode_list:
                return

            # 仅自动驾驶时间段内的日志进行全链路解析 
            if self.time_start_value > g_pilot_mode_list[-1][1] or self.time_split_value < g_pilot_mode_list[0][0]:
                return

            handle_time = g_pilot_mode_list[0][0] if g_pilot_mode_list[0][0] > self.time_start_value else self.time_start_value
            handle_time = int(handle_time % 100000)
            end_time = g_pilot_mode_list[-1][1] if g_pilot_mode_list[-1][1] < self.time_split_value else self.time_split_value
            end_time = int(end_time % 100000)
        else:
            handle_time = 0
            end_time = 99999

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
                                    self.load_one_log(one)
                                except Exception as e:
                                    print("the log {} in file {} is unexpect style! {}".format(line[start+9:], file_name, e))
                                    continue
                            
            handle_time += 1

        for path in ros_time_paths:
            with open(path, 'r') as fp:
                contents = fp.read()
                lines = contents.split("\n")

            for line in lines:
                sec_stamp = line.split('.')[0].split('[')[-1]
                if sec_stamp:
                    try:
                        if not g_test_mode and int(sec_stamp) < self.time_start_value: # alread handle
                            continue
            
                        if int(sec_stamp) < self.time_split_value:
                            start = line.find("#key-log#", 0, 128)
                            if start == -1:
                                continue
                        
                            one = json.loads(line[start+9:])
                            self.load_one_log(one)
                        else:
                            break
                    except Exception as e:
                        print("the log {} in file {} is unexpect style! {}".format(line, path, e))
                        continue

        if not g_test_mode:
            while g_pilot_mode_list and self.time_start_value > g_pilot_mode_list[0][1]:
                g_pilot_mode_list.pop(0)

    @get_time_used
    def load_logs(self):
        if self.handle_index == -1:
            st_atime = int(time.time())
            st_mtime = 0
            for path in self.input_paths:
                stat = os.stat(path)
                if st_atime > stat.st_atime:
                    st_atime = stat.st_atime
                if st_mtime <  stat.st_mtime:
                    st_mtime = stat.st_mtime
            if st_atime < int(time.time()) - 60:
                self.g_time_start_value = int(time.time()) - 5
            else:
                self.g_time_start_value = st_atime - 3  # before min access time 2 sec
            self.time_split_end = st_mtime + 2
            if st_mtime - st_atime > self.time_split_threshold:   # log 1.7M/s  30s about 50M
                print('log save {} secs, more than {}, handle a part!'.format(st_mtime-st_atime, self.time_split_threshold) )
                self.time_split_value = st_atime + self.time_split_threshold
                self.handle_index = 0
            else:
                self.time_split_value = self.time_split_end
            
        if len(self.input_paths):
            ros_time_paths=[]
            remote_paths=[]
            for path in self.input_paths:
                if 'remote' in path:
                    remote_paths.append(path)
                else:
                    ros_time_paths.append(path)

            ''' handel file one by one '''
            self.load_one_log_by_time(ros_time_paths, remote_paths)

        # 分片处理流程
        if self.handle_index >= 0:
            # 如果处理完了，恢复全量处理
            if self.time_split_value >= self.time_split_end:
                self.handle_index = -1
            else:
                self.time_start_value = self.time_split_value
                self.time_split_value += self.time_split_threshold
                self.handle_index += 1
        

    def get_topic_info(self, topic, data, record):
        if not topic['finish_flag']:
            data['succ'] = False
            data['wrong'] = '{} not match success'.format(topic['topic'])
            return

        # get time used of the topic between put to sub_recv
        pub_recv_time = topic['info']['recv_stamp'] - topic['info']['pub_stamp']
        recv_call_time = topic['info']['call_stamp'] - topic['info']['recv_stamp']
        data["use_time"] += pub_recv_time + recv_call_time
        data["path"].append({"type":"pub_recv", "node":topic['recv_node'].name, "use_time":pub_recv_time})
        data["path"].append({"type":"recv_call", "node":topic['recv_node'].name, "use_time":recv_call_time})

        if topic['send_node'].is_start_node:
            # 节点只有pub，数据源头，如果有beg，计算beg-end用时
            if topic['send_node'].beg_tag:
                beg_info = topic.get('beg_info', {})
                if beg_info:
                    beg_end_time = topic['info']['pub_stamp'] - beg_info["stamp"]
                    if beg_end_time > Constants.unit_stamp_sec * 1:  # if beg_end_time > 0.5s  print
                        print("add by liyl topic info: {}".format(topic))
                    u_spend = topic['info']['pub_utime'] - beg_info["utime"]
                    s_spend = topic['info']['pub_stime'] - beg_info["stime"]
                    w_spend = topic['info']['pub_wtime'] - beg_info["wtime"]
                    idle_spend = beg_end_time - u_spend - s_spend - w_spend    
                    u_percent, s_percent, w_percent, idle_percent = [round(x*1.0/beg_end_time,2) for x in (u_spend,s_spend,w_spend,idle_spend)]
                    # data["use_time"] += beg_end_time  del by liyl 20220609 not add to sum
                    data["path"].append({"type": "beg_end", "node": topic['send_node'].name, "use_time": beg_end_time})
                    data["path"].append({"type": "beg_end_cpu", "node": topic['send_node'].name, 
                    "u_spend": u_spend, "u_percent": u_percent, "s_spend": s_spend, "s_percent": s_percent, 
                    "w_spend": w_spend, "w_percent": w_percent, "idle_spend": idle_spend, "idle_percent": idle_percent})

            data['succ'] = True
            return

        if topic['uuid'] not in topic['send_node'].finish_dict:
            data['succ'] = False
            data['wrong'] = '{} not match success'.format(topic['send_node'].name)
            return

        sub_uuid_dict = topic['send_node'].finish_dict.get(topic['uuid'], {})
        callback_size = len(sub_uuid_dict)
        if callback_size == 0:
            data['succ'] = False
            data['wrong'] = 'the [pub_uuid:{}] not sub msg match, in node {}'.format(topic['uuid'], topic['send_node'].name)
            return
        index = 0
        for sub_topic_name, callback in sub_uuid_dict.items():
            index += 1
            # 当多于一个path时，需添加新的data
            # 我们让最后一个sub路径直接用老data，之前的做深拷贝
            if index < callback_size:
                pdata = copy.deepcopy(data)
                record.append(pdata)
            else:
                pdata = data

            if callback in all_link_topic_list[sub_topic_name]:
                topic_entity = all_link_topic_list[sub_topic_name][callback]
            else:
                data['succ'] = False
                data['wrong'] = '[uuid:{}] not in all_topic_list of [{}]'.format(callback, sub_topic_name)
                return

            if callback_size > 1:
                topic_entity['next_topic'] = topic
                pdata["split_path"].append(topic_entity['topic'])
                

            # get time used of the node between A topic recv_sub to B topic pub
            call_pub_time = topic['info']['pub_stamp'] - topic_entity['info']['call_stamp']
            u_spend = topic['info']['pub_utime'] - topic_entity['info']['sub_utime']
            s_spend = topic['info']['pub_stime'] - topic_entity['info']['sub_stime']
            w_spend = topic['info']['pub_wtime'] - topic_entity['info']['sub_wtime']
            idle_spend = call_pub_time - u_spend - s_spend - w_spend
            if idle_spend < 0:
                data['succ'] = False
                data['wrong'] = 'The time handle has error! node:{}, topic_uuid:{}'.format(topic['send_node'].name, topic['uuid'])
                return
            if call_pub_time > 1.5 * Constants.unit_stamp_sec:
                print('add by liyl 20220815 call_pub_time={}, topic={}, thread={} pub_uuid={}, sub_uuid={}'.format(
                    call_pub_time, topic['topic'], topic['thread'], topic['uuid'], topic_entity['uuid']))
                # import pdb; pdb.set_trace()

            u_percent, s_percent, w_percent, idle_percent = [round(x*1.0/call_pub_time,2) for x in (u_spend,s_spend,w_spend,idle_spend)]     
            pdata["use_time"] += call_pub_time
            pdata["path"].append({"type": "call_pub", "node": topic_entity['recv_node'].name, "use_time": call_pub_time})
            pdata["path"].append({"type": "call_pub_cpu", "node": topic_entity['recv_node'].name, 
            "u_spend": u_spend, "u_percent": u_percent, "s_spend": s_spend, "s_percent": s_percent, 
            "w_spend": w_spend, "w_percent": w_percent, "idle_spend": idle_spend, "idle_percent": idle_percent}) 
            
            ### TODO 目前只有man_beg, 后续该部分逻辑需要完善，增加man_end处理 
            if topic['send_node'].beg_tag:
                beg_info = topic.get('beg_info', {})
                if beg_info:
                    beg_end_time = topic['info']['pub_stamp'] - beg_info["stamp"]
                    if beg_end_time > Constants.unit_stamp_sec * 1:  # if beg_end_time > 0.5s  print
                        print("add by liyl topic info: {}".format(topic))
                    u_spend = topic['info']['pub_utime'] - beg_info["utime"]
                    s_spend = topic['info']['pub_stime'] - beg_info["stime"]
                    w_spend = topic['info']['pub_wtime'] - beg_info["wtime"]
                    idle_spend = beg_end_time - u_spend - s_spend - w_spend    
                    u_percent, s_percent, w_percent, idle_percent = [round(x*1.0/beg_end_time,2) for x in (u_spend,s_spend,w_spend,idle_spend)]
                    # data["use_time"] += beg_end_time  del by liyl 20220609 not add to sum
                    data["path"].append({"type": "beg_end", "node": topic['send_node'].name, "use_time": beg_end_time})
                    data["path"].append({"type": "beg_end_cpu", "node": topic['send_node'].name, 
                    "u_spend": u_spend, "u_percent": u_percent, "s_spend": s_spend, "s_percent": s_percent, 
                    "w_spend": w_spend, "w_percent": w_percent, "idle_spend": idle_spend, "idle_percent": idle_percent})
            
            self.get_topic_info(topic_entity, pdata, record)


    @get_time_used
    def analyze_key_info(self):    
        result = dict()
        wrong_count = 0
        target = "/chassis/command"
        #if g_test_mode:
        #   target = '/perception/fusion/obstacles'
        target_handle_complate = dict()  #{k=uuid, v=split topic completed}
        
        for topic_entity in all_link_topic_list[target].values():
            target_handle_complate[topic_entity['uuid']] = 0
            record = list()
            data = dict()
            data["use_time"] = 0
            data["path"] = []
            data["split_path"] = []
            record.append(data)
            self.get_topic_info(topic_entity, data, record)

            for data in record:
                if not data.get('succ', False):
                    wrong_count += 1
                    print(data.get('wrong', 'unknow reason'))
                    continue
                
                data["split_path_str"] = "_".join([x for x in data['split_path']])

                if data["split_path_str"] not in result:
                    result[data["split_path_str"]] = []
                result[data["split_path_str"]].append(data)
                    
                target_handle_complate[topic_entity['uuid']] += 1

                if self.last_timestamp < topic_entity['info']["recv_stamp"] - data['use_time'] - 1 *Constants.unit_stamp_sec:  #mod by liyl 20220414 delay 1 sec for test
                    self.last_timestamp = topic_entity['info']["recv_stamp"] - data['use_time'] - 1 *Constants.unit_stamp_sec


        match_one_num = 0
        match_two_num = 0
        no_match_num = 0  
        for uuid_time, match_num in target_handle_complate.items():
            if match_num == 0:
                no_match_num += 1
                continue
            elif match_num == 1:   
                match_one_num += 1
            elif match_num == 2:  # The case is ugly, maybe the sub list more than 2 in future
                match_two_num += 1
            
            del all_link_topic_list[target][uuid_time]

        print("total_command={}, match_two_paths={}, match_one_paths={} no_path={}".format(
            len(target_handle_complate), match_two_num, match_one_num, no_match_num))
            
        if self.last_timestamp < self.time_start_value * Constants.unit_stamp_sec:
            self.last_timestamp += self.time_start_value * Constants.unit_stamp_sec

        for topic_name in all_link_topic_list.keys():
            all_link_topic_temp = dict()
            for uuid, topic in all_link_topic_list[topic_name].items():
                if topic['info'].get('call_stamp', 2000000000) > self.last_timestamp:
                    all_link_topic_temp[uuid] = topic
                elif topic['send_node'] and topic['uuid'] in topic['send_node'].finish_dict:
                    del topic['send_node'].finish_dict[topic['uuid']]
                    if topic['uuid'] in topic['send_node'].beg_msg_dict:
                        del topic['send_node'].beg_msg_dict[topic['uuid']]
                    ## TODO：man_end增加后，需要清理 end_msg_dict
            all_link_topic_list[topic_name] = all_link_topic_temp
        
        ## add by liyl 20220901 for clear sub msg and beg msg
        for node_entry in all_link_node_list.values():
            node_entry.sub_msg_dict.clear()
            node_entry.beg_msg_dict.clear()

        self.results = result
        return 

    @staticmethod
    def get_usetime_pt(result, key="use_time"):
        size = len(result)
        size50 = int(size*0.5)
        size90 = int(size*0.9)
        size99 = int(size*0.99)

        if 'percent' in key:
            return result[size50][key], result[size90][key], result[size99][key]
        else:
            # 时间值，计算到毫秒，保留2位小数
            return round(result[size50][key]*1.0/1000000,2), round(result[size90][key]*1.0/1000000,2), round(result[size99][key]*1.0/1000000,2)

    def handle_cpu_time(self, split_data, save_data, mtype, node, type):
        split_data[mtype][node].sort(key=lambda s: s[type], reverse=False)
                    
        if node not in save_data[mtype]:
            save_data[mtype][node] = {}

        save_data[mtype][node][type] = {} 
        (save_data[mtype][node][type]["p50"], save_data[mtype][node][type]["p90"], save_data[mtype][node][type]["p99"]) \
         = self.get_usetime_pt(split_data[mtype][node], type)


    @get_time_used
    def save_result(self):
        for split_path_str in self.results:
            result = self.results[split_path_str]

            save_data = {}
            result.sort(key=lambda s: s["use_time"], reverse=False)
            (save_data["p50"], save_data["p90"], save_data["p99"]) = self.get_usetime_pt(result)

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
                        (save_data[mtype][node]["p50"], save_data[mtype][node]["p90"], save_data[mtype][node]["p99"]) = \
                        self.get_usetime_pt(split_data[mtype][node])
                else:
                    for node in split_data[mtype]:
                        self.handle_cpu_time(split_data, save_data, mtype, node, "u_spend")
                        self.handle_cpu_time(split_data, save_data, mtype, node, "u_percent")
                        self.handle_cpu_time(split_data, save_data, mtype, node, "s_spend")
                        self.handle_cpu_time(split_data, save_data, mtype, node, "s_percent")
                        self.handle_cpu_time(split_data, save_data, mtype, node, "w_spend")
                        self.handle_cpu_time(split_data, save_data, mtype, node, "w_percent")
                        self.handle_cpu_time(split_data, save_data, mtype, node, "idle_spend")
                        self.handle_cpu_time(split_data, save_data, mtype, node, "idle_percent")                    

            save_data["path"] = split_path_str
            save_data["count"] = len(result)
            save_data["timestamp"] = int(self.last_timestamp/1000000)
            self.car_info.set_car_info(save_data)
            #print(json.dumps(save_data, sort_keys=True, indent=4))
            with open(Constants.output_file, "a+") as fp:
                fp.write("{0}\n".format(json.dumps(save_data)))
        
        self.results=dict()

    def clear_input_files(self):
        if self.handle_index >= 0:
            return

        for file_path in self.input_paths:
            # 备份处理后的文件，到备份目录，防止remote文件重复，增加全量时间戳
            os.rename(file_path, '{}/{}_{}'.format(Constants.bak_dir, os.path.basename(file_path), int(time.time())))
            #os.remove(file_path)

        self.input_paths=list()


    def run_once(self):
        try:
            self.prepare_input_files()
            self.load_logs()
            self.analyze_key_info()
            self.save_result()
            self.clear_input_files()
        except Exception as e:
            print("run once error, {}".format(e))
            print ("exception happend")
            print ('str(Exception):\t', str(Exception))
            print ('str(e):\t', str(e))
            print ('repr(e):\t', repr(e))
            print ('traceback.format_exc():\n%s' % (traceback.format_exc()))  

    def run(self):
        print("开始分析")
        # dxc 读系统信息
        while True:
            start = time.time()
            self.run_once()
            end = time.time()
            print('run_once used time {}'.format(end-start))

            sleep_time = 2 - (end - start)
            if sleep_time > 0.3:
                time.sleep(sleep_time)


class NodeThread(threading.Thread):
    def __init__(self, topic, msg_type, call_back, parent=None):
        threading.Thread.__init__(self)
        rospy.Subscriber(topic, msg_type, call_back)
    def run(self):
        rospy.spin()


class Car_Status(object):
    def __init__(self):
        self.code_version = 'V2.6.0'
        self.plate = 'unknow'
        self.type = 'unknow'
        self.pilot_mode = 0
        if not g_test_mode:
            rospy.init_node('log_reslove')
            self.veh_state_thread = NodeThread("/system_master/SysVehicleState", BinaryData, self.recv_vstatus)
            self.get_car_info()
            self.veh_state_thread.start()
    
    def get_car_info(self):
        try:
            with open("/autocar-code/project_commit.txt") as fp:
                contents = fp.read().split("\n")

            self.code_version = contents[1][len("Version:"):]
        except Exception as e:
            print('get code_version failed: {}'.format(e))

        try:
            with open("/home/mogo/data/vehicle_monitor/vehicle_config.txt") as fp:
                contents = fp.read().split("\n")

            plate = contents[0].split(":")[-1]
            self.plate = plate.strip().strip("\"")

            brand = contents[1].split(":")[-1]
            self.type = brand.strip().strip("\"")

        except Exception as e:
            print('get vehicle_config failed: {}'.format(e))

    def set_car_info(self, data):
        data["code_version"] = self.code_version 
        data["carplate"] = self.plate 
        data["cartype"] = self.type

    def recv_vstatus(self, ros_msg):
        global g_pilot_mode_list

        g_vehicle_state = system_pilot_mode_pb2.SYSVehicleState()
        g_vehicle_state.ParseFromString(ros_msg.data)
        
        if self.pilot_mode != g_vehicle_state.pilot_mode:
            cur_time = int(time.time())
            print('autopilot mode changed to {}! cur_time:{}'.format(g_vehicle_state.pilot_mode, cur_time))
            if self.pilot_mode != 1: 
                print("start autopilot at time: {}".format(cur_time))
                if g_pilot_mode_list:
                    if cur_time == g_pilot_mode_list[-1][1]:
                        g_pilot_mode_list[-1][1] = cur_time+1
                    elif cur_time > g_pilot_mode_list[-1][1]:
                        g_pilot_mode_list.append([cur_time, cur_time+1])
                else:
                    g_pilot_mode_list.append([cur_time, cur_time+1])
            else:
                print("stop autopilot at time: {}".format(cur_time))
                g_pilot_mode_list[-1][1] = cur_time+1
        elif self.pilot_mode == 1 and g_pilot_mode_list:
            g_pilot_mode_list[-1][1] = int(time.time())+1

        self.pilot_mode = g_vehicle_state.pilot_mode


def main():
    if os.path.exists(Constants.input_dir) == False:
        os.makedirs(Constants.input_dir)
    if os.path.exists(Constants.tmp_dir) == False:
        os.mkdir(Constants.tmp_dir)
    if os.path.exists(Constants.bak_dir) == False:
        os.mkdir(Constants.bak_dir)
    if os.path.exists(Constants.output_dir) == False:
        os.mkdir(Constants.output_dir)

    for k, v in node_config.items():
        all_link_node_list[k] = Node_base(k)
        if v.get('pub', ''):
            all_link_topic_list[v['pub']] = dict()

    # log_reslove and all_link_delay_result save
    Log_handler().run()


if __name__ == '__main__':
    main()
