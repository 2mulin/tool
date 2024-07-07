# -*- coding: utf-8 -*-
import os
import platform
import socket
import fcntl
import struct


def get_current_username():
    if platform.system() == "Windows":
        return os.environ.get("USERNAME")
    return os.environ.get("USER")


def is_port_in_use(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("127.0.0.1", port))
        is_open = True
    except (TimeoutError, ConnectionRefusedError):
        is_open = False
    sock.close()
    return is_open


def get_ip_address(interface_name: str):
    """
    @brief 通过ioctl可以获取网卡IP; 详细原因只能去看手册: man netdevice
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 0x8915 表示SIOCGIFADDR, 网卡名称最长15字节
    ip = fcntl.ioctl(sock.fileno(), 0x8915, struct.pack('256s', bytes(interface_name[:15], "utf-8")))[20:24]
    sock.close()
    return socket.inet_ntoa(ip)


def compare_version(left_version: str, right_version: str):
    """
    @brief  比较两个mysql版本号, 版本号格式必须是"主版本号.子版本号.修正版本号"
    @return 如果 < 就返回-1, = 就返回0, > 就返回1
    """
    version1 = left_version.split('.')
    version2 = right_version.split('.')

    def num_cmp(s1, s2):
        if s1 < s2:
            return -1
        elif s1 == s2:
            return 0
        else:
            return 1
    
    for i in range(3):
        result = num_cmp(version1[i], version2[i])
        if result != 0:
            return result
    return 0
