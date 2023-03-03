#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import time
import psutil
import threading
import datetime
import traceback
import subprocess
import json
import logging
from logging.handlers import TimedRotatingFileHandler

LOG_PATH = "/home/mogo/data/log/monitor_cpu_mem_net/"
FILEBEAT_UPLOAD = '/home/mogo/data/log/filebeat_upload/'
VEHICLE_CONFIG_FILE = "/home/mogo/data/vehicle_monitor/vehicle_config.txt"
MONITOR_LOG_FILE = "monitor.log"
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
try:
    with open('/home/mogo/autopilot/share/launch/radar_config.json', 'r', encoding='utf-8') as f:
        RADAR_IP_DICT = json.load(f)
except:
    print("未找到radar_config.json")
MACHINE = ''
CAR_INFO = None
USEING_PORT = set()
sys_state_lock = threading.RLock()
iftop_lok = threading.RLock()
mpstat_lok = threading.RLock()
pidstat_lok = threading.RLock()
port_lock = threading.RLock()
node_info_lock = threading.RLock()


class Logger(object):
    """
    基于logging的二次封装
    """

    def __init__(self, logger_name, log_filename,
                 level=logging.INFO,
                 when="MIDNIGHT",
                 interval=1,
                 backup_count=15,
                 suffix="%Y-%m-%d",
                 log_formatter="[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d][%(process)d] - %(message)s"):
        self.logger = logging.getLogger(logger_name)
        self.formatter = logging.Formatter(log_formatter)
        self.handler = TimedRotatingFileHandler(log_filename, when=when, interval=interval, backupCount=backup_count,
                                                encoding="UTF-8", delay=False, utc=True)
        self.handler.suffix = suffix  # 设置切分后日志文件名的时间格式默认 filename+"." + suffix 如果需要更改需要改logging源码

        self.handler.setFormatter(self.formatter)
        logging.basicConfig(level=level, stream=None)
        self.logger.addHandler(self.handler)

    def debug(self, mes):
        self.logger.debug(mes)

    def info(self, mes):
        self.logger.info(mes)

    def warning(self, mes):
        self.logger.warning(mes)

    def error(self, mes):
        self.logger.error(mes)

    def critical(self, mes):
        self.logger.critical(mes)


logger = Logger("monitor", os.path.join(LOG_PATH, MONITOR_LOG_FILE), level=logging.INFO)


class Car_Status(object):
    def __init__(self):
        self.code_version = 'V2.6.0'
        self.plate = 'unknow'
        self.type = 'unknow'
        self.pilot_mode = 0
        self.get_car_info()

    def get_car_info(self):
        try:
            with open("/autocar-code/project_commit.txt") as fp:
                contents = fp.read().split("\n")

            self.code_version = contents[1][len("Version:"):]
        except Exception as e:
            pass

        try:
            with open("/home/mogo/data/vehicle_monitor/vehicle_config.txt") as fp:
                contents = fp.read().split("\n")

            plate = contents[0].split(":")[-1]
            self.plate = plate.strip().strip("\"")

            brand = contents[1].split(":")[-1]
            self.type = brand.strip().strip("\"")

        except Exception as e:
            pass

    def set_car_info(self, data):
        data["code_version"] = self.code_version
        data["carplate"] = self.plate
        data["cartype"] = self.type
        data["timestamp"] = int(time.time() * 1000)


def get_machine_name(net_if="eth0"):
    """
    获取机器ros名
    Returns:
        rosmaster/rosslave
    """
    machine_name = ""
    try:
        machine_ip = psutil.net_if_addrs()[net_if][0].address
        with open("/etc/hosts", "r") as fd:
            line = fd.readline()
            while line:
                if machine_ip in line:
                    line_str = line.split("\n")[0]
                    line_list = line_str.replace("\t", " ").split(" ")
                    machine_name = line_list[1]
                    break
                line = fd.readline()
    except Exception as e:
        logger.warning(e)
    return machine_name


def create_dir_path(dir_path):
    """
    创建目录
    Args:
        dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


def get_today_date():
    """
    获取今天的日期
    Args:
    Returns:
        日期(2022-10-12)
    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    return today


def get_mem_state():
    """
    获取内存占用比
    Returns:
        {"mem_percen": "11%"}
    """
    mem_percent = psutil.virtual_memory().percent
    return dict(mem_percent=str(mem_percent) + "%")


def get_net_pids():
    """
    获取网络链接pid列表
    Returns:
        [1, 2, 3]
    """
    nets = psutil.net_connections(kind="tcp")
    pids = list(set([net.pid for net in nets if net.pid]))
    return pids


def get_cpu_state():
    """
      获取cpu占用比
    Returns:
        {"cpu_percent":["9.1%","11%"], "total_cpu_percent":"10.5%"}
    """
    cpu_state_list = list()
    cpu_percent_list = psutil.cpu_percent(interval=0.5, percpu=True)
    for i in range(len(cpu_percent_list)):
        cpu_state_list.append(str(cpu_percent_list[i]) + "%")
    total_cpu_percent = str(psutil.cpu_percent(interval=0.5)) + "%"
    return dict(cpu_percent=cpu_state_list, total_cpu_percent=total_cpu_percent)


def get_processes_state():
    """
    获取运行中进程的状态
    Returns:
        {'28233': {'cmdline': ['/usr/sbin/zabbix_agentd:', 'collector', '[processing', 'data]'], 'status': 'running', 'cpu_percent': 0.0, 'cpu_num': 4, 'mem_percent': 0.011109379179016879, 'nice': 0}}
    """
    process_state_dict = dict()
    not_pids = [1]  # 不进行统计进程号列表
    for p in psutil.process_iter():
        try:
            pid = p.pid
            status = p.status()
            if pid in not_pids:
                continue
            process_state_info = {
                "cmdline": p.cmdline(),
                "status": status,
                "cpu_percent": p.cpu_percent(),
                "cpu_num": p.cpu_num(),
                "mem_percent": p.memory_percent(),
                "nice": p.nice(),
                # "net_connections": [{"laddr": str(con.laddr), "raddr": str(con.raddr)} for con in p.connections() if
                #                     con.raddr and con.status == 'ESTABLISHED']
            }
            if process_state_info.get("status", "") == "running":
                process_state_dict[str(pid)] = process_state_info
        except Exception as e:
            continue
    return process_state_dict


def get_cpu_consumption_3_pid():
    """
    循环获取消耗cpu最高的三个进程的信息
    Args:
        file_path: 日志文件路径
    Returns:
    """
    cmd_run = "ps -eo pid,pcpu,pmem,args --sort=-pcpu | head -n 4"
    out = subprocess.run(cmd_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
    out_lines = str(out.stdout, encoding="utf-8")
    return out_lines


def cpu_consumption_str_2_json(pid_str):
    """
    把cpu_consumption文本输出转化成字典
    """
    res = {}
    res['top_3_pids'] = dict()
    lines = pid_str.split('\n')
    titles = [i for i in lines[0].split(' ') if len(i) != 0]

    for i in range(1, 4):
        data = [part for part in lines[i].split(' ') if len(part) != 0]
        res['top_3_pids']['top_' + str(i) + '_process'] = dict(
            map(lambda key, val: (key, float(val)), titles[:3], data[:3]))
        res['top_3_pids']['top_' + str(i) + '_process']['PID'] = int(
            res['top_3_pids']['top_' + str(i) + '_process']['PID'])
        res['top_3_pids']['top_' + str(i) + '_process']['COMMAND'] = ' '.join(data[3:])
        CAR_INFO.set_car_info(res)
    return res


def get_sys_state():
    """
    获取系统状态
    Returns:
    """
    sys_state_dict = dict()
    sys_state_dict.update(get_mem_state())
    sys_state_dict.update(get_cpu_state())
    sys_state_dict["processes_state"] = get_processes_state()
    t = time.time()
    sys_state_dict["time"] = t
    sys_state_str = "[{}]:total_mem_percent:{},total_cpu_percent:{},cpu_percent:{},processes_state:{}\n".format(
        sys_state_dict.get("time", int(time.time() * 1000)),
        sys_state_dict.get("mem_percent", ""),
        sys_state_dict.get("total_cpu_percent", ""),
        sys_state_dict.get("cpu_percent", ""),
        sys_state_dict.get("processes_state", ""))
    cpu_consumption_str = get_cpu_consumption_3_pid()
    sys_state_str = sys_state_str + cpu_consumption_str

    del sys_state_dict["processes_state"]
    del sys_state_dict["time"]
    cpu_dict = dict()
    for i in range(len(sys_state_dict["cpu_percent"])):
        cpu_dict['cpu' + str(i + 1) + "(percent)"] = float(sys_state_dict["cpu_percent"][i][:-1])
    sys_state_dict["cpu_percent"] = cpu_dict
    sys_state_dict["mem_percent"] = float(sys_state_dict["mem_percent"][:-1])
    sys_state_dict["total_cpu_percent"] = float(sys_state_dict["total_cpu_percent"][:-1])
    sys_state_dict["machine"] = MACHINE

    sys_state_dict.update(cpu_consumption_str_2_json(cpu_consumption_str))
    return sys_state_str, sys_state_dict


def get_iftop_mes():
    """
    获取iftop命令的输出信息
    Returns:
    """
    cmd_run = "iftop -t -B -P -N -n -s 1"
    out = subprocess.run(cmd_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
    out_lines = str(out.stdout, encoding="utf-8")
    return out_lines


def write_logs(message, file_path, writ_lock):
    """
    写日志到文件
    Args:
        message: 文本内容
        file_path: 文件地址
        lock: 线程锁
    """
    writ_lock.acquire()
    with open(file_path, "a") as fd:
        fd.write(message)
    writ_lock.release()


def sys_state_loop(file_path, json_path):
    """
    循环获取系统状态
    Args:
        file_path: 日志文件路径
        json_path: 日志json文件路径
    Returns:
    """
    logger.info("获取系统状态开始....")
    while True:
        try:
            mes, mes_json = get_sys_state()
            with open(json_path, "a+") as fp:
                fp.write("{0}\n".format(json.dumps(mes_json)))
        except Exception as e:
            mes = e + "\n"
        write_logs(mes, file_path, sys_state_lock)
        time.sleep(2)


def get_cmd_out(cmd_line):
    """
    获取执行命令结果
    """
    try:
        out = subprocess.run(
            cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
    except Exception as e:
        logger.warning("执行命令{}时报错:{}".format(cmd_line, e))
        logger.warning('%s' % traceback.format_exc())
        out_lines = ""
    else:
        try:
            if out.returncode == 0:
                out_lines = str(out.stdout, encoding="utf-8")
            else:
                out_lines = ""
                logger.warning("执行命令{}失败:{}".format(cmd_line, str(out.stderr, encoding="utf-8")))
        except Exception as e:
            logger.warning("获取执行命令{}结果报错:{}".format(cmd_line, e))
            logger.warning('%s' % traceback.format_exc())
            out_lines = ""
    return out_lines


def get_cmd_pids(cmd):
    """
    根据执行命令获取进程号列表
    Args:
        cmd: 执行命令
    Returns:
        [pid1, pid2]
    """
    pids_list = list()
    ps_cmd = str("ps -ef | grep '{}' | grep -v grep ").format(cmd) + "| awk '{print $2}'"
    out_lines = get_cmd_out(ps_cmd)
    for line in out_lines.split("\n"):
        if line:
            try:
                pids_list.append(int(line.replace(" ", "")))
            except:
                continue
    return pids_list


def get_nodes_info():
    """
    获取所有node状态
    Returns:
        [{}]
    """
    node_pids = get_cmd_pids("__name:")
    node_info = list()
    try:
        p_objs = [psutil.Process(pid=i) for i in node_pids]
        for p in p_objs:
            p.cpu_percent(interval=None)
        time.sleep(1)
        for p in p_objs:
            node_info.append({
                "node_pid": p.pid,
                "node_cmd": " ".join(p.cmdline()),
                "node_parent_cmd": " ".join(psutil.Process(p.ppid()).cmdline()),
                "node_num_threads": len(p.threads()),
                "node_nice": p.nice(),
                "node_memory_percent": p.memory_percent(),
                "node_cpu_percent": p.cpu_percent(interval=None),
                "node_use_ports": list({pconn.laddr.port for pconn in p.connections() if pconn.laddr.port})
            })
    except Exception as e:
        logger.warning("获取node状态报错:{}".format(e))
        logger.warning('%s' % traceback.format_exc())
    return node_info


def get_port_process(port_set):
    try:
        net_process_info = [{"pid": sconn.pid,
                             "cmd": " ".join(psutil.Process(sconn.pid).cmdline()),
                             "laddr_port": sconn.laddr.port if sconn.laddr and sconn.laddr.port else "",
                             "raddr_ip": sconn.raddr.ip if sconn.raddr and sconn.raddr.ip else "",
                             "raddr_port": sconn.raddr.port if sconn.raddr and sconn.raddr.port else "",
                             } for sconn in [sconn for sconn in psutil.net_connections() if sconn.pid] if
                            sconn.laddr.port in port_set]
    except Exception as e:
        logger.error("获取端口进程信息报错:{}".format(e))
        logger.warning('%s' % traceback.format_exc())
        return []
    else:
        return net_process_info


def port_process_loop(file_path):
    """
    循环获取端口进程信息
    Args:
        file_path: 日志目录
    """
    logger.info("获取端口进程信息开始....")
    while True:
        try:
            res = get_port_process(USEING_PORT)
            line = "{}{}{}:{}{}".format("[", str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), "]",
                                        json.dumps(res),
                                        "\n")
            write_logs(line, file_path, port_lock)
        except Exception as e:
            logger.error("获取端口进程信息报错:{}".format(e))
            logger.warning('%s' % traceback.format_exc())
        time.sleep(5)


def get_process_info_loop(file_path):
    """
    循环获取node信息
    Args:
        file_path: 日志目录
    """
    logger.info("获取节点信息开始....")
    while True:
        try:
            res = get_nodes_info()
            line = "{}{}{}:{}{}".format("[", str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), "]",
                                        json.dumps(res),
                                        "\n")
            write_logs(line, file_path, node_info_lock)
        except Exception as e:
            logger.error("获取node信息报错:{}".format(e))
            logger.warning('%s' % traceback.format_exc())
        time.sleep(4)


def iftop_mes_loop(file_path):
    """
    循环获取iftop信息
    Args:
        file_path: 日志文件路径
    Returns:
    """
    global USEING_PORT
    logger.info("获取iftop信息开始....")
    while True:
        first_line = "==========================================" \
                     + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) \
                     + "==========================================\n"
        try:
            iftop_mes = get_iftop_mes()
            mes = first_line + iftop_mes
        except Exception as e:
            mes = first_line + e
        write_logs(mes, file_path, iftop_lok)
        for line in iftop_mes.split("\n"):
            if "=>" in line:
                try:
                    USEING_PORT.add(int(line.split(":")[1].split(" ")[0]))
                except Exception as e:
                    logger.error("获取本机流量端口报错:{}".format(e))
        time.sleep(0.1)


def get_pidstat_mes():
    """
        获取pidstat命令的输出信息
        Returns:
    """
    cmd_run = "pidstat -u |sort -r -n -k 8|head -10"
    out = subprocess.run(cmd_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
    out_lines = str(out.stdout, encoding="utf-8")
    return out_lines


def pidstat_loop(file_path):
    """
    循环获取pidstat信息
    Args:
        file_path: 日志文件路径
    Returns:
    """
    logger.info("获取pidstat信息开始....")
    while True:
        first_line = "==========================================" \
                     + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) \
                     + "==========================================\n"
        try:
            pidstat_mes = first_line + "              UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command\n" + get_pidstat_mes()
            mes = pidstat_mes
        except Exception as e:
            mes = first_line + e
        write_logs(mes, file_path, pidstat_lok)
        time.sleep(2)


def get_mpstat_mes():
    """
        获取mpstat命令的输出信息
        Returns:
    """
    cmd_run = "mpstat -P ALL 1 1"
    out = subprocess.run(cmd_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
    out_lines = str(out.stdout, encoding="utf-8")
    out_lines = out_lines[:out_lines.find('平均')]
    out_lines = out_lines[:out_lines.find('Average')]
    return out_lines


def mpstat_to_json(mp_stat):
    res = {}
    res['mpstat'] = dict()
    lines = mp_stat.split('\n')
    titles = [i for i in lines[2].split(' ') if len(i) != 0]
    for line in lines[3:]:
        if len(line) == 0:
            break
        data = [i for i in line.split(' ') if len(i) != 0]
        res['mpstat']['cpu_' + data[1]] = dict(map(lambda key, val: (key, float(val)), titles[2:], data[2:]))
        CAR_INFO.set_car_info(res)
        res["machine"] = MACHINE
    return res


def mpstat_loop(file_path, json_path):
    """
    循环获取mpstat信息
    Args:
        file_path: 日志文件路径
    Returns:
    """
    logger.info("获取mpstat信息开始....")
    while True:
        first_line = "==========================================" \
                     + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) \
                     + "==========================================\n"
        try:
            mpstat_mes = get_mpstat_mes()
            mes = mpstat_mes
            mes_json = mpstat_to_json(mes)
            with open(json_path, "a+") as fp:
                fp.write("{0}\n".format(json.dumps(mes_json)))
        except Exception as e:
            mes = first_line + e
        write_logs(mes, file_path, mpstat_lok)
        time.sleep(2)


def get_car_plate_brand():
    """
    从配置获取车牌和品牌
    Returns:
       'TAXI001', 'df'
    """
    plate, brand = "", ""
    with open(VEHICLE_CONFIG_FILE, "r") as fd:
        config_lines = fd.readlines()
        try:
            for line in config_lines:
                if "plate" in line:
                    plate = line.split("\n")[0].split(":")[1].split('"')[1]
                    continue
                if "brand" in line:
                    brand = line.split("\n")[0].split(":")[1].split('"')[1]
        except Exception as e:
            logger.error("从配置获取车牌和品牌报错:{}".format(e))
            logger.warning('%s' % traceback.format_exc())
    return plate, brand.lower()


def get_car_type():
    """
    获取车辆型号2x/6x
    Returns:
        2x/6x
    """
    count = 0
    with open("/etc/hosts", "r") as fd:
        lines = fd.readlines()
        for line in lines:
            if line[0] == "#":
                continue
            if "ros" in line:
                count = count + 1
        car_type = "2x" if count < 6 else "6x"
    return car_type


def ping_thread(log_dir_path):
    logger.info("获取ping_radar信息开始....")
    _, car_brand = get_car_plate_brand()
    car_type = get_car_type()
    for radar_name, radar_ip in RADAR_IP_DICT[car_brand][car_type].items():
        cmd_run = "ping -D -c 86400 -i 1 {0} >> {1}/{2}.log 2>&1 &".format(radar_ip, log_dir_path, radar_name)
        subprocess.Popen(cmd_run, shell=True, executable="bash", stdout=None, stderr=None)


def main():
    global MACHINE
    global CAR_INFO
    MACHINE = get_machine_name()
    CAR_INFO = Car_Status()
    today_date = get_today_date()
    log_dir_path = LOG_PATH + today_date
    create_dir_path(log_dir_path)
    create_dir_path(FILEBEAT_UPLOAD)
    sys_state_log = log_dir_path + "/sys_state.log"
    iftop_log = log_dir_path + "/iftop.log"
    pidstat_log = log_dir_path + "/pidstat.log"
    mpstat_log = log_dir_path + "/mpstat.log"
    port_process_log = os.path.join(log_dir_path, "port_process.log")
    node_info_log = os.path.join(log_dir_path, "node_info.log")

    mpstat_json = FILEBEAT_UPLOAD + "mpstat_json.log"
    sys_state_json = FILEBEAT_UPLOAD + 'sys_state_json.log'

    t1 = threading.Thread(target=sys_state_loop, args=(sys_state_log, sys_state_json))
    t2 = threading.Thread(target=iftop_mes_loop, args=(iftop_log,))
    t3 = threading.Thread(target=pidstat_loop, args=(pidstat_log,))
    t4 = threading.Thread(target=mpstat_loop, args=(mpstat_log, mpstat_json))
    t5 = threading.Thread(target=port_process_loop, args=(port_process_log,))
    t6 = threading.Thread(target=get_process_info_loop, args=(node_info_log,))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    # t5.start()
    t6.start()
    ping_thread(log_dir_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("监控报错:{}".format(e))
        logger.warning('%s' % traceback.format_exc())
