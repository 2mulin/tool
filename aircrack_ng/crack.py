# -*- coding: utf-8 -*-
"""
开始运行抓包, 破解逻辑...
"""

import subprocess

def run(interface: str):
    """
    @brief: 破解工具启动函数, 破解完成后将破解的WIFI名称-密码存放到文件中;
    @param interface 可以监听的网卡接口
    @return 成功True, 失败False
    """
    command = f"airmon-ng start {interface}"
    complete_proc = subprocess.run(command, capture_output=True, check=False)
    if complete_proc.returncode != 0:
        return False
    command = f"airmon-ng check {interface}"
    complete_proc = subprocess.run(command, capture_output=True, check=False)
    if complete_proc.returncode != 0:
        return False

    # 指定只抓包1分钟, 并且将内容输出到csv文件中, 用来分析各wifi的信号强度, 再来选择目标破解...
    command = f"airodump-ng {interface}mon -w output"
    complete_proc = subprocess.run(command, capture_output=True, check=False)
    if complete_proc.returncode != 0:
        return False
        
    return True
