# -*- coding: utf-8 -*-
"""
@date   2024/1/6
@author mulin
"""

import os
import time

import password_dict
import airmon_ng


def create_data_dir(path: str)->bool:
    """
    创建指定目录
    """
    # 工作产生的一些数据文件
    data_path = f"{path}/data"
    if os.access(data_path, os.F_OK):
        print(f"[info] {data_path} already exists, no need create again!")
        return True

    try:
        os.mkdir(data_path, 0o755)
    except FileNotFoundError as e:
        print(f"[error] Failed to create data directory! reason: {e}")
        return False
    return True


def main()->bool:
    """
    主要工作流程
    """
    # 检查环境是否可以运行airmon-ng    
    if not airmon_ng.check_env():
        return False

    # 创建一个目录， 存放工作过程中产生的数据文件
    work_dir = os.getcwd()
    data_path = f"{work_dir}/data"
    if not create_data_dir(data_path):
        return False

    # 如果当前密码字典文件不存在， 则创建
    password_dict_file = f"{data_path}/phone_num.txt"
    if not os.access(password_dict_file, os.F_OK):
        if not password_dict.generate_phone_num(password_dict_file):
            print("[error] Failed to generate password file! ")
            return False
    
    return True


if __name__ == '__main__':
    start_time = time.perf_counter()
    success = main()
    elapse = int(time.perf_counter() - start_time)
    second = int(time.perf_counter() - start_time) % 60
    minute = int((second / 60) % 60)
    hour = int((second / 60) / 60)
    if success:
        print(f"[finish] success, elapse {hour}h{minute}m{second}s")
    else:
        print(f"[finish] failed, elapse {hour}h{minute}m{second}s")
