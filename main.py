# -*- coding: utf-8 -*-
"""
@date   2024/1/6
@author mulin
"""

import os

import password_dict


def main():
    """
    主要工作流程
    """
    work_dir = os.getcwd()
    # 工作产生的一些数据文件
    data_path = f"{work_dir}/data"
    if os.access(data_path, os.F_OK):
        print(f"{data_path} already exists, prevent overwriting, program exit!")
        return 1

    try:
        os.mkdir(data_path, 0o755)
    except FileNotFoundError as e:
        print(f"Failed to create data directory! reason: {e}")

    password_dict_file = f"{data_path}/phone_num.txt"
    if not password_dict.generate_phone_num(password_dict_file):
        print("Failed to generate password file! ")
        return 1
    
    
    return 0


if __name__ == '__main__':
    if main() == 1:
        exit(1)
