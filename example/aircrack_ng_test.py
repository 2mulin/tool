# -*- coding: utf-8 -*-
"""
@date   2024/5/23
@author mulin
@brief  aircrack_ng模块的简单代码示例, 将文件复制到上层目录即可运行, 在这一层目录无法运行(会找不到包);
"""

import os
import sys
import time
import logging


import password_dict
import aircrack_ng

log_handler = logging.StreamHandler(stream=sys.stderr)
log_formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.ERROR)

logging.basicConfig(filename='aircrack_ng_test.log', 
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S", 
    encoding='utf-8',
    level=logging.INFO)
logger = logging.getLogger("aircrack_ng_test")
logger.addHandler(log_handler)



def create_data_dir(path: str)->bool:
    """
    判断路径是否存在, 不存在就创建
    """
    # 工作产生的一些数据文件
    data_path = f"{path}/data"
    if os.access(data_path, os.F_OK):
        logger.info(f"{data_path} already exists, no need create again!")
        return True

    try:
        os.mkdir(data_path, 0o755)
    except FileNotFoundError as e:
        logger.error(f"Failed to create data directory! reason: {e}")
        return False
    return True


def main()->bool:
    """
    主要工作流程
    """
    # 检查环境是否可以运行aircrack_ng
    if not aircrack_ng.check_env():
        logger.error("The environmental check failed! exit")
        return False

    # 在当前工作目录, 创建文件夹存放工作过程中产生的数据文件
    work_dir = os.getcwd()
    data_path = f"{work_dir}/data"
    if not create_data_dir(data_path):
        return False

    # 如果当前密码字典文件不存在, 则创建
    password_dict_file = f"{data_path}/phone_num.txt"
    if not os.access(password_dict_file, os.F_OK):
        if not password_dict.generate_phone_num(password_dict_file):
            logger.error("Failed to generate password file!")
            return False
    
    return True


if __name__ == '__main__':
    is_success: bool = main()
    if is_success:
        logger.info(f"[finish] success")
    else:
        logger.error(f"[finish] failed")
