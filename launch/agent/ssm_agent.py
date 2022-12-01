import os
import json
import pprint
import sys
import yaml
import time
import psutil
import signal
import pickle
import logging
import datetime
import requests
import traceback
import subprocess
import multiprocessing
from logging.handlers import TimedRotatingFileHandler
from http.server import HTTPServer, SimpleHTTPRequestHandler

IP = "0.0.0.0"  # 监听IP，配置项
PORT = 8081  # 监听端口，配置项
TOKEN = ""
ROSMASTER_IP_PORT = "http://192.168.1.102:8080"  # 会根据主机不同改变
MASTER_PORT = 8080  # master 端口号
REPORT_MESSAGE = {}
REPORT_URL = "/report_config"
HEART_BEAT_URL = "/heartbeat_status"
MACHINE_INFO_FILE = "/home/mogo/autopilot/share/launch/agent/machine_info.byte"
AGENT_LOG_PATH = "/home/mogo/data/log/ssm_agent_log"
AGENT_LOG_FILE = "agent.log"
if not os.path.exists(AGENT_LOG_PATH):
    os.mkdir(AGENT_LOG_PATH)
PROJECT_COMMIT_FILE = "/autocar-code/project_commit.txt"
VEHICLE_CONFIG_FILE = "/home/mogo/data/vehicle_monitor/vehicle_config.txt"
AGENT_CONFIG_FILE = "/home/mogo/autopilot/share/launch/agent/agent_config.json"
LAUNCH_LOG_SHELL = "/home/mogo/autopilot/share/launch/add_log_config.sh"
LAUNCH_PATH = "/home/mogo/autopilot/share/launch"
ABS_PATH = LAUNCH_PATH
ROS_LOG_DIR = os.path.join("/home/mogo/data/log/", datetime.datetime.now().strftime('%Y%m%d'))
KILLED_LAUNCH_NODE_LIST = list()

# 进程锁,在对全局配置读写时进行加锁
machine_info_lock = multiprocessing.Lock()
killed_launch_node_lock = multiprocessing.Lock()


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
        self.handler = TimedRotatingFileHandler(log_filename,
                                                when=when,
                                                interval=interval,
                                                backupCount=backup_count,
                                                encoding="UTF-8",
                                                delay=False,
                                                utc=True)
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


logger = Logger("agent", os.path.join(AGENT_LOG_PATH, AGENT_LOG_FILE), level=logging.DEBUG)


def write_with_lock(file_name, data, lock):
    """
    同步写数据
    Args:
        file_name: 文件名
        data: 数据
        lock: 进程锁
    """
    lock.acquire()
    with open(file_name, "wb") as fd:
        pickle.dump(data, fd)
    lock.release()


def read_with_lock(file_name, lock):
    """
    同步读数据
    Args:
        file_name: 文件名
        lock: 进程锁
    Returns:
        data
    """
    if os.path.exists(file_name):
        lock.acquire()
        with open(file_name, "rb") as fd:
            data = pickle.load(fd)
        lock.release()
    else:
        data = dict()
    return data


def write_killed_launch_node_with_lock(launch_node, append=True, lock=killed_launch_node_lock):
    """
    同步操作KILLED_LAUNCH_NODE_LIST
    Args:
        launch_node: launch node name
        append: True:新增, False: 删除
        lock: 进程锁
    """
    lock.acquire()
    global KILLED_LAUNCH_NODE_LIST
    if append:
        if launch_node not in KILLED_LAUNCH_NODE_LIST:
            KILLED_LAUNCH_NODE_LIST.append(launch_node)
    else:
        if launch_node in KILLED_LAUNCH_NODE_LIST:
            try:
                KILLED_LAUNCH_NODE_LIST.remove(launch_node)
            except Exception as e:
                logger.warning("KILLED_LAUNCH_NODE_LIST 删除launch_node:{}时报错:{}".format(launch_node, str(e)))
                logger.warning('%s' % traceback.format_exc())
    lock.release()


class MyRequests(object):
    def __init__(self, token=TOKEN, timeout=5):
        """
        :param token: 请求token
        """
        self.token = {"Authorization": token}
        self.headers = {"Content-Type": "application/json"}
        self.headers.update(self.token)
        self.timeout = timeout

    def get(self, url, params=None, timeout=0, **kwargs):
        """
        :param url: 请求地址
        :param timeout: 超时时间
        :param params: 请求路径参数
        :param kwargs: 其他参数
        :return:
        """
        return requests.get(url, params, headers=self.token, timeout=timeout if timeout > 0 else self.timeout, **kwargs)

    def post(self, url, data=None, timeout=0, **kwargs):
        """
        :param url: 请求地址
        :param timeout: 超时时间
        :param data: 请求body参数
        :param kwargs: 其他参数
        :return:
        """
        return requests.post(url, data, headers=self.headers, timeout=timeout if timeout > 0 else self.timeout,
                             **kwargs)

    def put(self, url, data=None, **kwargs):
        """
        :param url: 请求地址
        :param timeout: 超时时间
        :param data: 请求body参数
        :param kwargs: 其他参数
        :return:
        """
        return requests.put(url, data, headers=self.headers, timeout=self.timeout, **kwargs)

    def delete(self, url, **kwargs):
        """
        :param url: 请求地址
        :param timeout: 超时时间
        :param kwargs: 其他参数
        :return:
        """
        return requests.delete(url, headers=self.token, timeout=self.timeout, **kwargs)

    def options(self, url, **kwargs):
        """
        :param url: 请求地址
        :param timeout: 超时时间
        :param kwargs: 其他参数
        :return:
        """
        return requests.options(url, headers=self.token, timeout=self.timeout, **kwargs)

    def get_result(self, res):
        try:
            json_res = res.json()
        except Exception as e:
            logger.warning('%s' % traceback.format_exc())
            return {"code": 1, "message": "解析结果失败：%s" % str(e), "data": {"msg": "解析结果失败：%s" % str(e)}}
        return json_res


myrequest = MyRequests()


class RefactorHttpServer(SimpleHTTPRequestHandler):
    """
    自定义一个 HTTP 请求处理器
    """

    def do_response_json(self):
        """
        请求返回application/json格式
        """
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def fail_response(self, data={}, message="fail message"):
        """
        失败数据响应输出流
        Args:
            data: 数据
            message: 消息内容
        Returns:
            响应输出流
        """
        self.do_response_json()
        result = {"code": 1, "data": data, "message": message}
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def success_response(self, data={}, message="ok"):
        """
        成功数据响应输出流
        Args:
            data: 数据
            message: 消息内容
        Returns:
            响应输出流
        """
        self.do_response_json()
        result = {"code": 0, "data": data, "message": message}
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def do_GET(self):
        """
        处理get请求
        """
        # 获取路由
        url_str = self.path
        route_path = url_str.split("?")[0]
        if len(url_str) > len(route_path):
            request_data_str = url_str.split("?")[1]
            request_data = {request_par.split("=")[0]: request_par.split("=")[1] for request_par in
                            request_data_str.split("&")}
        # 根据路由不同处理
        if route_path == "/test":
            # 处理流程
            # handler_func()
            state, res = 0, {"code": 2}
            if state == 0:
                self.success_response(data=res)
            else:
                self.fail_response(message=res)
        else:
            self.fail_response(message='%s 路由处理不存在!' % route_path)

    def do_POST(self):
        """
        处理post请求
        """
        # 获取路由
        route_path = self.path
        # 获取请求数据
        request_data = self.rfile.read(int(self.headers["content-length"]))
        if request_data:
            request_data = json.loads(request_data)
        # 根据路由不同处理
        if route_path == "/set_agent_config":
            # 设置agent配置
            state, res = set_agent_config(request_data)
            if state == 0:
                self.success_response()
            else:
                self.fail_response(message=res)

        elif route_path == "/get_agent_config":
            # 获取agent配置
            self.success_response(data=REPORT_MESSAGE)
        else:
            self.fail_response(message='%s 路由处理不存在!' % route_path)


def http_server():
    """
    启动 http server
    """
    logger.info("START AGENT SERVER IP:{},Port:{}".format(IP, PORT))
    server = HTTPServer((IP, PORT), RefactorHttpServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


def set_agent_config(request_data):
    """
    将master下发的要启动的node写到配置里
    Args:
        request_data: 请求数据
    Returns:
        state, message
    """
    state, message = 0, ""
    try:
        target_launch_node_list = request_data.get("node_config_list", [])
        logger.info("master下发的node list:{}".format(str(target_launch_node_list)))
        data = read_with_lock(MACHINE_INFO_FILE, machine_info_lock)
        data["target_launch_node_list"] = target_launch_node_list
        write_with_lock(MACHINE_INFO_FILE, data, machine_info_lock)
    except Exception as e:
        logger.error("将master下发的要启动的node写到配置里时报错:%s" % e)
        logger.warning('%s' % traceback.format_exc())
        state = 1
        message = e
    return state, message


def get_cmd_out(cmd_line):
    """
    获取执行命令结果
    """
    try:
        out = subprocess.run(
            cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
    except Exception as e:
        logger.warning("获取执行命令{}结果时报错:{}".format(cmd_line, e))
        logger.warning('%s' % traceback.format_exc())
        out_lines = ""
    else:
        if out.returncode == 0:
            out_lines = str(out.stdout, encoding="utf-8")
        else:
            out_lines = ""
    return out_lines


def get_image_version():
    """
    获取镜像版本
    Returns:
    """
    with open(PROJECT_COMMIT_FILE, 'r', encoding='utf-8', errors='ignore') as fd:
        results = fd.read()
        for line in results.split('\n'):
            if 'Version' == line.split(':')[0]:
                image_version = line.split(':')[1].strip()
                break
    return image_version


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
        logger.error("获取机器ros名报错:%s" % e)
        logger.warning('%s' % traceback.format_exc())
    return machine_name


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


def get_ssm_master_ip():
    """
    获取SSM Master IP
    """
    ros_line_list = list()
    with open("/etc/hosts", "r") as fd:
        lines = fd.readlines()
        for line in lines:
            if line[0] == "#":
                continue
            if "ros" in line:
                ros_line_list.append(line)
    if len(ros_line_list) == 1:
        line_str = ros_line_list[0]
    elif len(ros_line_list) == 2:
        for line in ros_line_list:
            if "rosslave" in line:
                line_str = line
                break
    elif len(ros_line_list) == 6:
        for line in ros_line_list:
            if "rosslave-106" in line:
                line_str = line
                break
    else:
        line_str = ""
    line_list = line_str.replace("\t", " ").split(" ")
    ip = line_list[0].replace(" ", "")
    return ip


def get_hardware_state():
    """
    获取硬件信息
    """
    hardware_state = dict()
    try:
        hardware_state = {
            "platform": sys.platform,
            "total_cpu_used": str(psutil.cpu_percent(interval=0.5)) + "%",
            "total_mem_used": str(psutil.virtual_memory().percent) + "%",
            "total_disk_used": str(psutil.disk_usage("/").percent) + "%"
        }
    except Exception as e:
        logger.error("获取硬件信息报错:{}".format(e))
        logger.warning('%s' % traceback.format_exc())
    return hardware_state


"""
launch/node 操作
"""


def get_nodes_list():
    """
    获取ros node 列表
    """
    cmd_line = "rosnode list"
    out_lines = get_cmd_out(cmd_line)
    node_list = out_lines.split("\n")
    node_list.remove("")
    return node_list


def get_pkg_path():
    """
    获取 ros package 路径
    Returns:
    """
    package_path_dict = dict()
    cmd_line = "rospack list"
    out_lines = get_cmd_out(cmd_line)

    for line in out_lines.split("\n"):
        line_list = line.split(" ")
        if len(line_list) == 2:
            package_path_dict[line_list[0].replace(
                " ", "")] = line_list[1].replace(" ", "")
    data = read_with_lock(MACHINE_INFO_FILE, machine_info_lock)
    data["package_path_dict"] = package_path_dict
    write_with_lock(MACHINE_INFO_FILE, data, machine_info_lock)


def yaml_to_dict(yaml_path):
    """
    yaml文件内容转换成dict格式
    Args:
        yaml_path: yaml文件路径
    Returns:
        {}
    """
    datas = dict()
    with open(yaml_path, encoding="utf-8") as f:
        try:
            datas = yaml.load(f, Loader=yaml.FullLoader)  # 将文件的内容转换为字典形式
        except Exception as e:
            logger.error("yaml文件{}内容转换成dict格式报错:{}".format(yaml_path, e))
            logger.warning('%s' % traceback.format_exc())
    return datas


def get_launch_nodes(launch_cmd):
    """
    获取launch里的node
    Args:
        launch_cmd: package xx.launch
    Returns:
        [node1, node2]
    """
    node_list = list()
    cmd_line = "roslaunch --nodes " + launch_cmd
    out_lines = get_cmd_out(cmd_line)
    for line in out_lines.split("\n"):
        if line:
            if line.startswith("/"):
                node_list.append(line.replace(" ", ""))
    return node_list


def get_launch_files(launch_path):
    """
    获取launch里的launch文件路径
    Args:
        launch_path: launch文件的绝对路径
    Returns:
        [launch1, launch2]
    """
    launch_list = list()
    cmd_line = "roslaunch --files " + launch_path
    out_lines = get_cmd_out(cmd_line)
    for line in out_lines.split("\n"):
        if line:
            if line.startswith("/"):
                launch_list.append(line.replace(" ", ""))
    return launch_list


def create_config():
    """
    将机器信息记录
    """
    machine_info = read_with_lock(MACHINE_INFO_FILE, machine_info_lock)
    package_path_dict = machine_info.get("package_path_dict", {})
    machine = get_machine_name()
    with open(AGENT_CONFIG_FILE, "r", encoding="utf8") as fp:
        agent_config = json.load(fp)
    report_dict = {
        "desc": agent_config.get("desc", "Agent config"),
        "author": agent_config.get("author", ""),
        "last_modify": agent_config.get("last_modify", ""),
        "protocal_version": agent_config.get("protocal_version", ""),
        "image_version": get_image_version(),
        "src": agent_config.get("src", ""),
        "machine": machine,
        "timestamp": time.time(),
    }
    launch_config_list = agent_config.get("MAP_agent_status_info", [])
    report_dict["MAP_image_config"] = launch_config_list
    car_type = get_car_type()
    car_plate, car_brand = get_car_plate_brand()
    launch_node_dict = dict()
    local_node_config = list()
    for launch_config in launch_config_list:
        if car_brand in launch_config.get("car_type", []):
            if machine in launch_config.get("machine", {}).get(car_type, {}).get("must", []):
                launch_name = launch_config.get("launch_name", "")
                package = launch_config.get("package", "")
                package_path = package_path_dict.get(package, "")
                path = launch_config.get("path", "")
                if (not package) and (not path):
                    launch_cmd = launch_name
                elif path:
                    if path.startswith("/"):  # path为绝对路径则优先使用path路径
                        launch_cmd = os.path.join(path, launch_name)
                    else:
                        launch_cmd = os.path.join(
                            package_path, path, launch_name)
                elif not path:
                    launch_cmd = "{} {}".format(package, launch_name)
                # if launch_name in launch_node_dict:
                #     continue
                node_list = get_launch_nodes(launch_cmd)
                for node in node_list:
                    # (launch_name, node)作为唯一标识,防止不同launch对应相同node
                    launch_node_dict[(launch_name, node)] = {
                        "launch_name": launch_name,
                        "launch_cmd": launch_cmd
                    }
                local_node_config.append({
                    "node_name_list": node_list,
                    "launch_name": launch_name})
    report_dict["local_node_config"] = local_node_config
    machine_info["report_message"] = report_dict  # 启动上报master信息(固定)
    # 启动launch name 与 launch_cmd node对应关系(固定)
    machine_info["launch_node_dict"] = launch_node_dict
    machine_info["agent_work_result"] = {}
    machine_info["target_launch_node_list"] = []
    write_with_lock(MACHINE_INFO_FILE, machine_info, machine_info_lock)
    return machine_info


def send_report(report_dict):
    """
    向master上报配置
    Args:
        report_dict: 上报配置
    """
    while True:
        try:
            url = ROSMASTER_IP_PORT + REPORT_URL
            logger.debug(url)
            res = myrequest.post(url, json=report_dict, timeout=10)
            logger.debug(str(myrequest.get_result(res)))
        except Exception as e:
            logger.warning("向master上报配置报错:%s" % e)
            logger.warning('%s' % traceback.format_exc())
            time.sleep(2)
            continue
        break


def get_cmd_pids(cmd):
    """
    根据执行命令获取进程号列表
    Args:
        cmd: 执行命令
    Returns:
        [pid1, pid2]
    """
    pids_list = list()
    ps_cmd = str("ps -ef | grep '{}' | grep -v grep ").format(cmd) + \
             "| awk '{print $2}'"
    # print(ps_cmd)
    out_lines = get_cmd_out(ps_cmd)
    for line in out_lines.split("\n"):
        if line:
            try:
                pids_list.append(int(line.replace(" ", "")))
            except:
                continue
    return pids_list


def get_last_node_name(node_name):
    """
    从/aaa/bbb/ccc/xxx 得到xxx
    """
    if "/" in node_name:
        return node_name.split("/")[-1]
    else:
        return node_name


def get_current_nodes_pid(launch_node_dict):
    """
    获取本地要启动的launch与node进程号
    Args:
        launch_node_dict:{("launch_name_XXX", "node_name_xxx"): {"launch_name": "XXX",
                                                                 "launch_cmd": "xxxx"
                                                                }
                        }
    Returns:
    """
    current_nodes_pid_info = dict()
    for launch_node_name, launch_info in launch_node_dict.items():
        try:
            node_name_last = get_last_node_name(launch_node_name[1])
            node_pids = get_cmd_pids("__name:={}".format(node_name_last))
            launch_pids = get_cmd_pids(launch_info.get(
                "launch_cmd") + " --launch-node " + launch_node_name[1])
            current_nodes_pid_info[launch_node_name] = {"node_pid": node_pids, "launch_pid": launch_pids,
                                                        "launch_name": launch_info.get("launch_name", ""),
                                                        "launch_cmd": launch_info.get("launch_cmd", "")}
        except Exception as e:
            logger.error("获取本地要启动的launch与node:{}进程号时报错:{}".format(e, str(launch_node_name)))
            logger.warning('%s' % traceback.format_exc())
            continue

    return current_nodes_pid_info


def start_node(node_name, launch_name, launch_node_dict, package_path_dict):
    """
    根据node名启动node
    Args:
        node_name: node名
        launch_name: launch名
        launch_node_dict: node与launch的启动关系
        package_path_dict: 包与绝对地址关系
    Returns:
        0,{}
    """
    status, res = 1, {}
    key = (launch_name, node_name)
    if key in launch_node_dict:
        node_info = launch_node_dict.get(key, {})
        if isinstance(node_info, dict):
            launch_name = node_info.get("launch_name", "")
            launch_cmd = node_info.get("launch_cmd", "")
            launch_cmd_node = "roslaunch --wait " + \
                              launch_cmd + " --launch-node " + node_name
            try:
                if " " in launch_cmd:
                    package_name = launch_cmd.split(" ")[0]
                    package_path = package_path_dict.get(package_name, "")
                    launch_abs_path = os.path.join(package_path, launch_name)
                    if not os.path.exists(launch_abs_path):
                        launch_abs_path = os.path.join(package_path, "launch", launch_name)
                else:
                    launch_abs_path = launch_cmd
                launch_files_list = get_launch_files(launch_abs_path)
                if len(launch_files_list) > 1:
                    for launch_file in launch_files_list:
                        if launch_file == launch_abs_path:
                            continue
                        else:
                            if node_name in get_launch_nodes(launch_file):
                                launch_abs_path = launch_file
                                break
                # launch_cmd_new = "roslaunch " + launch_cmd
                shell_cmd = '. {} {} INFO {}'.format(LAUNCH_LOG_SHELL, launch_abs_path, node_name)
                shell_process = subprocess.Popen(shell_cmd, shell=True, executable="bash", stdout=None,
                                                 stderr=None, env={"ABS_PATH": ABS_PATH, "ROS_LOG_DIR": ROS_LOG_DIR})
                node_last_name = get_last_node_name(node_name)
                # launch_name_file = launch_abs_path.split("/")[-1].split(".")[0]
                rosconsole_config_file = os.path.join(ABS_PATH, "config", node_last_name + "_INFO_console.config")
                ros_python_log_config_file = os.path.join(ABS_PATH, "config",
                                                          "python_logging_" + node_last_name + ".conf")
                logger.debug(
                    "launch log,shell_cmd:{}, shell_pid:{}, ROSCONSOLE_CONFIG_FILE:{}, ROS_PYTHON_LOG_CONFIG_FILE:{}".format(
                        shell_cmd, str(shell_process.pid), rosconsole_config_file, ros_python_log_config_file))
                os.environ['ROSCONSOLE_CONFIG_FILE'] = rosconsole_config_file
                os.environ['ROS_PYTHON_LOG_CONFIG_FILE'] = ros_python_log_config_file
            except Exception as e:
                logger.warning('%s' % traceback.format_exc())
            for i in range(3):
                launch_process = subprocess.Popen(launch_cmd_node, shell=True, executable="bash", stdout=None,
                                                  stderr=None)

                launch_process_pid = launch_process.pid
                logger.info("start node, launch_cmd_node:{}, launch_pid:{}".format(launch_cmd_node, launch_process_pid))
                if psutil.pid_exists(launch_process_pid):
                    res = {
                        "launch_pid": launch_process_pid,
                        "node_pid": 0,
                        "launch_name": launch_name,
                        "launch_cmd": launch_cmd
                    }
                    status = 0
                    break
        else:
            # 没有对应的启动方式
            status, res = 1, {}
    else:
        # 启动节点失败
        status, res = 1, {}
    return status, res


def kill_node(launch_pid, node_pid):
    """
    关闭节点
    Args:
        launch_pid: launch 进程号
        node_pid: node进程号
    Returns:
        0/1 0:成功， 1:失败
    """
    status = 0
    if psutil.pid_exists(node_pid):
        for signal_code in [signal.SIGINT, signal.SIGTERM, signal.SIGKILL]:
            os.kill(launch_pid, signal_code)
            info = os.waitpid(launch_pid, os.WSTOPPED)
            if psutil.pid_exists(launch_pid):
                continue
            else:
                if psutil.pid_exists(node_pid):
                    for signal_code_node in [signal.SIGINT, signal.SIGTERM, signal.SIGKILL]:
                        os.kill(node_pid, signal_code_node)
                        node_info = os.waitpid(node_pid, os.WSTOPPED)
                        if psutil.pid_exists(node_pid):
                            continue
                        else:
                            break
                    else:
                        status = 1
                else:
                    break
        else:
            status = 1
    return status


def agent_worker():
    """
    agent work 进程，根据目标node与当前状态结合上次的处理结果，处理node启停并记录操作结果
    Returns:
        存储记录
    """
    # 记录agent_worker进程号
    agent_worker_pid = os.getpid()
    machine_info_dict = read_with_lock(
        MACHINE_INFO_FILE, machine_info_lock)
    machine_info_dict["agent_worker_pid"] = agent_worker_pid
    write_with_lock(MACHINE_INFO_FILE,
                    machine_info_dict, machine_info_lock)

    while True:
        try:
            machine_info_dict = read_with_lock(
                MACHINE_INFO_FILE, machine_info_lock)
            package_path_dict = machine_info_dict.get("package_path_dict", {})
            launch_node_dict = machine_info_dict.get("launch_node_dict", {})
            agent_work_result = machine_info_dict.get("agent_work_result", {})
            target_launch_node_list = machine_info_dict.get(
                "target_launch_node_list", [])
            current_nodes_pid_info = get_current_nodes_pid(launch_node_dict)
            current_nodes_runnig_pid_info = dict()
            for current_launch_node in current_nodes_pid_info:
                # 获取真正运行的node
                if len(current_nodes_pid_info.get(current_launch_node, {}).get("node_pid", [])) > 0:
                    current_nodes_runnig_pid_info[current_launch_node] = current_nodes_pid_info.get(current_launch_node)
            target_launch_node_dict = dict()
            for target_launch_node in target_launch_node_list:
                target_node_name = target_launch_node.get("node_name")
                target_launch_name = target_launch_node.get("launch_name")
                if target_node_name and target_launch_name:
                    target_launch_node_dict[(target_launch_name, target_node_name)] = target_launch_node.get(
                        "launch_name", "")
            """
            遍历本地所有node:
                是否在目标中:
                    当前是否有：
                        agent是否有
                            处理
            1. agent(无)+当前(无)+目标(有) ->启动并记录;
            2. agent(无)+当前(有)+目标(有) ->不处理(人为启动);
            3. agent(有)+当前(无)+目标(有) ->删除agent记录(人为关闭);
            4. agent(有)+当前(有)+目标(有) ->a.当agent记录进程属于当前进程列表->不处理;
                                         ->b.当agent记录进程不属于当前进程列表->删除agent记录(人为启动);
            5. agent(无)+当前(无)+目标(无) ->不处理;
            6. agent(无)+当前(有)+目标(无) ->不处理(人为启动);
            7. agent(有)+当前(无)+目标(无) ->删除agent记录(人为关闭)
            8. agent(有)+当前(有)+目标(无) ->a.当agent记录进程属于当前进程列表->关闭进程并删除agent记录;
                                         ->b.当agent记录进程不属于当前进程列表->不处理(人为启动);
            """
            for launch_node_name, launch_info in launch_node_dict.items():
                launch_name = launch_node_name[0]
                node_name = launch_node_name[1]
                # node是否在目标中
                if launch_node_name in target_launch_node_dict:
                    # 判断当前node状态是否在运行；
                    if launch_node_name in current_nodes_runnig_pid_info:
                        # agent是否记录
                        if launch_node_name in agent_work_result:
                            # 4.agent(有) + 当前(有) + 目标(有)
                            # a.当agent记录进程属于当前进程列表->不处理;
                            # b.当agent记录进程不属于当前进程列表->删除agent记录(人为启动);
                            if agent_work_result.get(launch_node_name).get(
                                    "node_pid") not in current_nodes_runnig_pid_info.get(launch_node_name).get(
                                "node_pid"):
                                try:
                                    write_killed_launch_node_with_lock(launch_node_name, append=True)
                                    agent_work_result.pop(launch_node_name, "")
                                except:
                                    pass
                        else:
                            # 2. agent(无)+当前(有)+目标(有) ->不处理(人为启动);
                            pass
                    else:
                        if launch_node_name in agent_work_result:
                            # 3. agent(有)+当前(无)+目标(有)
                            #                           当launch pid 存在时->保留，因为是launch启动node一直失败
                            #                           否则—>删除agent记录(人为关闭)
                            try:
                                if agent_work_result.get(launch_node_name, {}).get("launch_pid"):
                                    pass
                                else:
                                    write_killed_launch_node_with_lock(launch_node_name, append=True)
                                    agent_work_result.pop(launch_node_name, "")
                            except:
                                pass
                        else:
                            # 1. agent(无)+当前(无)+目标(有) ->启动并记录;
                            status, res = start_node(node_name, launch_name, launch_node_dict, package_path_dict)
                            if status == 0:
                                agent_work_result[launch_node_name] = res

                else:
                    # 判断当前node状态是否在运行；
                    if launch_node_name in current_nodes_runnig_pid_info:
                        # agent是否记录
                        if launch_node_name in agent_work_result:
                            # 8.agent(有) + 当前(有) + 目标(无)
                            # a.当agent记录进程属于当前进程列表->关闭进程并删除agent记录;
                            # b.当agent记录进程不属于当前进程列表->不处理(人为启动);
                            if agent_work_result.get(launch_node_name).get(
                                    "node_pid") in current_nodes_runnig_pid_info.get(
                                launch_node_name).get("node_pid"):
                                try:
                                    node_pid = agent_work_result.get(
                                        launch_node_name).get("node_pid")
                                    launch_pid = agent_work_result.get(
                                        launch_node_name).get("launch_pid")
                                    status = kill_node(launch_pid, node_pid)
                                    # if status == 0:
                                    write_killed_launch_node_with_lock(launch_node_name, append=True)
                                    agent_work_result.pop(launch_node_name, "")
                                except:
                                    pass
                        else:
                            # 6. agent(无)+当前(有)+目标(无) ->不处理(人为启动);
                            pass
                    else:
                        if launch_node_name in agent_work_result:
                            # 7. agent(有)+当前(无)+目标(无) ->删除agent记录(人为关闭)
                            try:
                                write_killed_launch_node_with_lock(launch_node_name, append=True)
                                agent_work_result.pop(launch_node_name, "")
                            except:
                                pass
                        else:
                            # 5. agent(无)+当前(无)+目标(无) ->不处理;
                            pass
        except Exception as e:
            logger.error("agent worker报错:{}".format(e))
            logger.warning('%s' % traceback.format_exc())
        time.sleep(10)


def heart_beat():
    """
    心跳函数
        1.更新主机中运行的nodo当前状态;
        2.上报节点节点状态;
    """
    global ROSMASTER_IP_PORT
    heart_beat_url = ROSMASTER_IP_PORT + HEART_BEAT_URL
    while True:
        try:
            heart_beat_info = dict()
            machine_info_dict = read_with_lock(
                MACHINE_INFO_FILE, machine_info_lock)
            agent_worker_pid = machine_info_dict.get("agent_worker_pid", 0)
            report_message = machine_info_dict.get("report_message", {})
            heart_beat_info.update({"desc": "本文件用于Agent上报心跳状态使用",
                                    "image_version": report_message.get("image_version", ""),
                                    "protocal_version": report_message.get("protocal_version", ""),
                                    "src": report_message.get("src", ""),
                                    "machine": report_message.get("machine", ""),
                                    "timestamp": time.time()})
            MAP_agent_status_info = dict()
            MAP_agent_status_info["hardware_state"] = get_hardware_state()
            launch_node_dict = machine_info_dict.get("launch_node_dict", {})
            agent_work_result = machine_info_dict.get("agent_work_result", {})
            # 将被agent work 杀掉的launch node 从agent work result去除
            logger.debug("KILLED_LAUNCH_NODE_LIST:{}, agent_work_result:{}".format(str(KILLED_LAUNCH_NODE_LIST),
                                                                                   str([i for i in agent_work_result])))
            for killed_launch_node in KILLED_LAUNCH_NODE_LIST:
                if killed_launch_node in agent_work_result:
                    agent_work_result.pop(killed_launch_node, "")
                    write_killed_launch_node_with_lock(killed_launch_node, append=False)
            current_nodes_pid_info = get_current_nodes_pid(launch_node_dict)
            for current_launch_node_name, current_node_info in current_nodes_pid_info.items():
                try:
                    launch_pid_list = current_node_info.get("launch_pid", [])
                    if len(launch_pid_list) > 0:
                        for launch_pid in launch_pid_list:
                            launch_pid_info = psutil.Process(launch_pid)
                            if agent_worker_pid == launch_pid_info.parent().pid:
                                agent_work_result[current_launch_node_name] = {"node_pid": 0,
                                                                               "launch_pid": launch_pid,
                                                                               "launch_cmd": current_node_info.get(
                                                                                   "launch_cmd", ""),
                                                                               "launch_name": current_node_info.get(
                                                                                   "launch_name", "")}
                                node_process_list = launch_pid_info.children()
                                if len(node_process_list) > 0:
                                    for node_process in node_process_list:
                                        node_process_pid = node_process.pid
                                        if isinstance(node_process_pid, int):
                                            agent_work_result[current_launch_node_name]["node_pid"] = node_process_pid
                                            break
                except Exception as e:
                    continue
            target_launch_node_list = machine_info_dict.get(
                "target_launch_node_list", [])
            current_nodes_runnig_pid_info = dict()
            for current_launch_node in current_nodes_pid_info:
                # 获取真正运行的node
                if len(current_nodes_pid_info.get(current_launch_node, {}).get("node_pid", [])) > 0:
                    current_nodes_runnig_pid_info[current_launch_node] = current_nodes_pid_info.get(current_launch_node)
            node_list = list()
            for launch_node_name, launch_info in launch_node_dict.items():
                state = 0
                # node_name = launch_node_name[1]
                # 判断当前node状态是否在运行；
                if launch_node_name in current_nodes_runnig_pid_info:
                    # agent是否记录
                    if launch_node_name in agent_work_result:
                        # 4.agent(有) + 当前(有)
                        # a.当agent记录进程属于当前进程列表->3(运行态);
                        # b.当agent记录进程不属于当前进程列表->6(人为启动);
                        if agent_work_result.get(launch_node_name).get(
                                "node_pid") not in current_nodes_runnig_pid_info.get(launch_node_name).get("node_pid"):
                            state = 6
                        else:
                            state = 3
                    else:
                        # 2. agent(无)+当前(有) ->6(人为启动);
                        state = 6
                else:
                    if launch_node_name in agent_work_result:
                        # 3. agent(有)+当前(无)
                        #                   agent中node进程不存在->5(启动失败)
                        #                   否则->7(人为关闭)
                        if agent_work_result.get(launch_node_name, {}).get("node_pid", 0) == 0:
                            state = 5
                        else:
                            state = 7
                    else:
                        # 1. agent(无)+当前(无) ->0(未启动);
                        state = 0
                node_list.append({"node_name": launch_node_name[1],
                                  "launch_name": launch_info.get("launch_name", ""),
                                  "state": state})
            MAP_agent_status_info["node_list"] = node_list
            MAP_agent_status_info["target_list"] = target_launch_node_list

            heart_beat_info["MAP_agent_status_info"] = MAP_agent_status_info

            machine_info_dict["agent_work_result"] = agent_work_result
            machine_info_dict["current_nodes_pid_info"] = current_nodes_pid_info
            logger.debug("heart beat will write_with_lock")
            write_with_lock(MACHINE_INFO_FILE, machine_info_dict, machine_info_lock)
            logger.info(str(heart_beat_info))
        except Exception as e:
            logger.warning("heart beat报错:{}".format(e))
            logger.warning('%s' % traceback.format_exc())
            continue
        try:
            res = myrequest.post(heart_beat_url,
                                 json=heart_beat_info, timeout=1)
            response_re = myrequest.get_result(res)
        except Exception as e:
            logger.warning("发送心跳请求异常:{}".format(e))
            logger.warning('%s' % traceback.format_exc())
            continue
        time.sleep(2)


def main():
    global ROSMASTER_IP_PORT
    global REPORT_MESSAGE
    global ABS_PATH
    global ROS_LOG_DIR
    try:
        if sys.argv[1]:
            ABS_PATH = sys.argv[1]
        if sys.argv[2]:
            ROS_LOG_DIR = sys.argv[2]
    except:
        pass
    ROSMASTER_IP_PORT = "http://" + get_ssm_master_ip() + ":" + str(MASTER_PORT)
    # 获取package路径并记录
    get_pkg_path()
    # 生成配置
    machine_info = create_config()
    REPORT_MESSAGE = machine_info.get('report_message', {})
    # 上报配置
    send_report(REPORT_MESSAGE)
    heart_beat_process = multiprocessing.Process(target=heart_beat)
    http_server_beat_process = multiprocessing.Process(target=http_server)
    work_process = multiprocessing.Process(target=agent_worker)
    work_process.start()
    http_server_beat_process.start()
    time.sleep(1)
    heart_beat_process.start()


if __name__ == "__main__":
    main()