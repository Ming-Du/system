import os
import time
import psutil
import threading
import datetime
import subprocess

LOG_PATH = "/home/mogo/data/log/monitor_cpu_mem_net/"
sys_state_lock = threading.RLock()
iftop_lok = threading.RLock()


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
        sys_state_dict.get("time", time.time()),
        sys_state_dict.get("mem_percent", ""),
        sys_state_dict.get("total_cpu_percent", ""),
        sys_state_dict.get("cpu_percent", ""),
        sys_state_dict.get("processes_state", ""))
    return sys_state_str


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


def sys_state_loop(file_path):
    """
    循环获取系统状态
    Args:
        file_path: 日志文件路径
    Returns:
    """
    while True:
        try:
            mes = get_sys_state()
        except Exception as e:
            mes = e + "\n"
        write_logs(mes, file_path, sys_state_lock)
        time.sleep(1)


def iftop_mes_loop(file_path):
    """
    循环获取iftop信息
    Args:
        file_path: 日志文件路径
    Returns:
    """
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


def main():
    today_date = get_today_date()
    log_dir_path = LOG_PATH + today_date
    create_dir_path(log_dir_path)
    sys_state_log = log_dir_path + "/sys_state.log"
    iftop_log = log_dir_path + "/iftop.log"
    t1 = threading.Thread(target=sys_state_loop, args=(sys_state_log,))
    t2 = threading.Thread(target=iftop_mes_loop, args=(iftop_log,))
    t1.start()
    t2.start()


if __name__ == "__main__":
    main()
