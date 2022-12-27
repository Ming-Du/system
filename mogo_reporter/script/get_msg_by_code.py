#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import yaml


def yaml_to_dict(yaml_path):
    """
    yaml文件内容转换成dict
    Args:
        yaml_path: yaml 文件目录
    Returns:
        yaml的 dict 格式
    """
    data_dict = dict()
    with open(yaml_path) as f:
        data_dict = yaml.load(f)
    return data_dict


def gen_report_msg(file_name, code, src="test", org_msg=""):
    """
    根据code与配置文件获取对应的code信息
    Args:
        file_name: yaml 配置文件名
        code:
        src:
        org_msg:
    Returns:
        code信息json格式
    """
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/../../mogo_messages/nodes/' + os.path.basename(
        file_name)
    if not os.path.exists(file_path):
        print(file_path)
        return '{}'
    res = dict()
    yaml_dict = yaml_to_dict(file_path)
    for level, code_list in yaml_dict.items():
        for code_info in code_list:
            if code == code_info.get("code"):
                cur_time = int(time.time())
                res = {
                    "timestamp": {
                        "sec": cur_time,
                        "nsec": int((time.time() - cur_time) * 1000000000)
                    },
                    "src": src,
                    "level": level,
                    "code": code,
                    "msg": code_info.get("msg", "") + '; ' + org_msg,
                    "result": code_info.get("result", []),
                    "action": code_info.get("action", [])
                }
    return json.dumps(res)


if __name__ == '__main__':
    file_name = sys.argv[1]
    code = sys.argv[2]
    print(str(gen_report_msg(file_name, code)))
