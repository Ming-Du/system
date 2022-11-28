# -*- coding: utf-8 -*-

import os
import pickle
import pprint


def read_with_lock(file_name):
    """
    同步读数据
    Args:
        file_name: 文件名
        lock: 进程锁
    Returns:
        data
    """
    if os.path.exists(file_name):
        with open(file_name, "rb") as fd:
            data = pickle.load(fd)

    else:
        data = dict()
    return data


if __name__ == "__main__":
    pprint.pprint(read_with_lock("machine_info.byte"))
