# -*- coding: utf-8 -*-
"""
检查当前操作系统环境, 能否使用airmon-ng工具链
"""

import subprocess


def check()->bool:
    """
    检查当前环境, 能否使用arimon-ng工具链, 有没有能监听的网卡
    """
    is_ok = True
    try:
        complete_proc = subprocess.run("airmon-ng", capture_output=True, check=True)
        if complete_proc.returncode != 0:
            is_ok = False
        output = complete_proc.stdout.decode()
        # 如果airmon-ng的输出去掉空白行后, 只有一行(PHY Interface Driver Chipset), 表示没有可以监听的网卡
        str_list = [ str for str in output.split('\n') if len(str) ]
        if len(str_list) == 1:
            is_ok = False
    except FileNotFoundError:
        is_ok = False
    except Exception:
        is_ok = False
    return is_ok
