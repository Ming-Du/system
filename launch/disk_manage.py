import os
import time
import yaml
import shutil
import datetime
import traceback

YAML_PATH = '/home/mogo/data/vehicle_monitor/disk_manage_conf.yaml'


def today_ago_date(n: int):
    """
    距离今天前n天的日期
    Args:
        n: 天数
    Returns:
        日期
    """
    today = datetime.datetime.now()
    # 计算偏移量
    offset = datetime.timedelta(days=-n)
    # 当前时间前n天
    re_date = today + offset
    # 日期格式化
    # today = today.strftime('%Y-%m-%d')
    re_date = re_date.strftime('%Y-%m-%d')
    return re_date


def is_path_timeout(path, days):
    """
    判断路径的修改是否在几天前
    Args:
        path: 绝对路径
        days: 超时天数
    Returns:
        True/False
    """
    update_time = time.strftime("%Y-%m-%d", time.localtime(get_file_update_time(path)))
    if datetime.datetime.strptime(update_time, "%Y-%m-%d") < datetime.datetime.strptime(
            today_ago_date(days), "%Y-%m-%d"):
        return True
    else:
        return False


def yaml_to_dict(yaml_path):
    """
    yaml文件内容转换成dict格式
    Args:
        yaml_path: yaml文件路径
    Returns:
        yaml字典格式
    """
    datas = dict()
    try:
        with open(yaml_path, encoding="utf-8") as f:
            datas = yaml.load(f, Loader=yaml.FullLoader)  # 将文件的内容转换为字典形式
    except Exception as e:
        print("磁盘管理yaml配置文件格式有问题, Exception:{}, Traceback:{}".format(e, traceback.format_exc()))
    return datas


def get_file_update_time(file_path):
    """
    获取路径更新时间
    Args:
        file_path: 文件路径
    Returns:
        文件更新时间戳
    """
    if os.path.exists(file_path):
        return os.path.getmtime(file_path)
    else:
        return 0


def child_dirs_files(dir):
    """
    目录中的文件夹与文件
    Args:
        dir: 目录地址
    Returns:
        文件夹绝对路径列表, 文件绝对路径列表
    """
    dirs_list = list()
    files_list = list()
    try:
        # 获取所有的文件
        files_list = [os.path.join(dir, name) for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
        # 获取所有的文件夹
        dirs_list = [os.path.join(dir, name) for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]
    except Exception as e:
        print("获取目录{}中的文件夹与文件报错, Exception:{}, Traceback:{}".format(dir, e, traceback.format_exc()))
    return dirs_list, files_list


def rm_files(files_list=[]):
    """
    删除文件/文件夹
    Args:
        files_list: 要删除的路径列表
    """
    for path in files_list:
        if os.path.exists(path):
            if os.path.isfile(path):
                try:
                    os.remove(path)  # 这个可以删除单个文件，不能删除文件夹
                except Exception as e:
                    print("删除文件{}报错, Exception:{}, Traceback:{}".format(path, e, traceback.format_exc()))
                    continue
            elif os.path.isdir(path):  # 删除目录
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    print("删除目录{}报错, Exception:{}, Traceback:{}".format(path, e, traceback.format_exc()))
                    continue


def clear_file(dir, depth, clear_days, not_clear_files_dirs_list):
    """
    清理文件
    Args:
        dir: 目录, 绝对路径
        depth: 扫描深度
        clear_days: 清除前clear_days数据
        not_clear_files_dirs_list: 不出清除文件/目录集合
    Returns:
        {"code":0, "message":"", "data":""}
        其中：code 0为成功， 1为失败
    """
    ret = {"code": 0, "message": "", "data": ""}
    if os.path.exists(dir) and os.path.isdir(dir):
        try:
            handle_dir_list = [dir]  # 需要处理的目录
            not_clear_files_dirs_set = set(not_clear_files_dirs_list)
            rm_set = set()
            for i in range(depth):
                for dir_name in handle_dir_list:  # 循环处理需要处理的目录
                    handle_dir_list.remove(dir_name)  # 在待处理目录列表中删除本次处理的目录
                    if is_path_timeout(dir_name, clear_days):  # 该目录已经超时，将目录下的所有文件夹与文件添加到删除集合
                        child_dirs_list, child_files_list = child_dirs_files(dir_name)
                        tmp_rm_set = set(child_files_list + child_dirs_list).difference(not_clear_files_dirs_set)
                        rm_set = rm_set.union(tmp_rm_set)
                    else:  # 该目录未超时，将目录下超时的文件夹与文件添加到删除集合， 并获取下次需要处理的目录
                        child_dirs_list, child_files_list = child_dirs_files(dir_name)
                        for child_dir in set(child_dirs_list).difference(not_clear_files_dirs_set):
                            if is_path_timeout(child_dir, clear_days):
                                rm_set.add(child_dir)
                            else:
                                handle_dir_list.append(child_dir)  # 将未超时目录添加到待处理目录
                        for child_file in set(child_files_list).difference(not_clear_files_dirs_set):
                            if is_path_timeout(child_file, clear_days):
                                rm_set.add(child_file)
            rm_files(list(rm_set))
            print("清理目录{}完成.".format(dir))
        except Exception as e:
            ret["code"] = 1
            ret["message"] = e
            print("清理目录{}报错, Exception:{}, Traceback:{}".format(dir, e, traceback.format_exc()))
    return ret


def main():
    print("开始磁盘清理.")
    start_time = time.time()
    yaml_path = YAML_PATH
    conf_dict = yaml_to_dict(yaml_path)
    gloabl_conf = conf_dict.get("global", {})
    gloabl_clear_days = gloabl_conf.get("clear_days", 15)
    gloabl_depth = gloabl_conf.get("depth", 2)
    gloabl_not_clear_files_dirs = gloabl_conf.get("not_clear_files_dirs", [])
    gloabl_size = gloabl_conf.get("size", 5000)
    dir_conf_list = conf_dict.get("dirs", [])
    for dir_conf in dir_conf_list:
        dir = dir_conf.get("dir", "")
        depth = dir_conf.get("depth") if dir_conf.get("depth") else gloabl_depth
        clear_days = dir_conf.get("clear_days") if dir_conf.get("clear_days") else gloabl_clear_days
        size = dir_conf.get("size") if dir_conf.get("size") else gloabl_size
        not_clear_files_dirs = dir_conf.get("not_clear_files_dirs") if dir_conf.get(
            "not_clear_files_dirs") else gloabl_not_clear_files_dirs
        # 清理文件
        clear_file(dir, depth, clear_days, set(not_clear_files_dirs))
    print("完成磁盘清理,耗时:{}s.".format(str(time.time() - start_time)))


if __name__ == "__main__":
    main()
