#-*- coding: utf-8 -*-
"""
@brief 全局变量的声明
"""

import os
import sys
import logging
import subprocess


if "logger" not in globals():
    logger = None
if "g_initialized" not in globals():
    g_initialized = False


def _log_init():
    """
    @brief 日志初始化
    """
    global logger
    if logger == None:
        log_handler = logging.StreamHandler(stream=sys.stderr)
        log_formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        log_handler.setFormatter(log_formatter)
        log_handler.setLevel(logging.ERROR)

        logging.basicConfig(filename='net_tool.log', 
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S", 
            encoding='utf-8',
            level=logging.INFO)
        logger = logging.getLogger("net_tool")
        logger.addHandler(log_handler)
    return True


def _iptables_init(client_ip: str):
    """
    @brief 防火墙初始化
    如果没有就做一些初始化工作, 比如说完成iptables的设置;
    因为用scapy发包, 一旦对端回应, 由于本地Linux内核网络栈没有相应的数据结构, 
    那么本机网络就会直接返回RST包, 这就不是预期内的效果;
    """
    command = f"iptables -A OUTPUT -p tcp -s {client_ip} -j DROP".split()
    # check=False表示程序执行失败, 不抛异常; 但是如果command指令找不到,还是抛异常....所以这里判断不够...
    try:
        complete_proc = subprocess.run(command, capture_output=True, check=False)
    except Exception as e:
        logger.error(f"set iptables failed: {e}")
        return False
    if complete_proc.returncode:
        logger.error(f"set iptables failed: {complete_proc.stderr}")
        return False
    return True


def is_running_as_root():
    """
    @brief 判断当前用户是否是root, 否则无法使用scapy, iptables
    """
    return os.geteuid() == 0


def init():
    """
    @brief 对模块进行初始化工作
    """
    if not _log_init():
        sys.exit(1)
    if not is_running_as_root():
        logger.error(f"Must be run with the root user!")
        sys.exit(1)
    if not _iptables_init():
        sys.exit(1)
    global g_initialized
    g_initialized = True


def shutdown():
    """
    @brief 关闭并且刷新日志文件
    """
    global g_initialized
    if g_initialized:
        logging.shutdown()
