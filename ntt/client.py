#-*- coding: utf-8 -*-
"""
@date: 2024/3/17
@author: mulin
"""


import socket
import scapy.all as scapy
from .define import logger


def syn_send(ip_address, port):
    """
    @brief 发送TCP SYN报文到指定的IP地址和端口
    @param ip_address 目标IP地址
    @param port 目标端口号
    """
    syn_packet = scapy.IP(dst=ip_address) / scapy.TCP(dport=port, flags='S')
    try:
        scapy.send(syn_packet, verbose=False)
    except Exception as e:
        logger.error(f"sending TCP SYN packet failed: {e}")
        return False
    return True


def tcp_connect(server_ip: str, server_port: int):
    """
    @brief 建立TCP连接请求(全连接)
    @param server_ip 服务端的IP
    @param server_port 服务端的Port
    @return 成功建立后的客户端socket, 失败返回None
    """
    server = (server_ip, server_port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(server)
    except ConnectionRefusedError as cre:
        logger.error(f"Connection refused: {cre}")
        return None
    except TimeoutError as te:
        logger.error(f"Connection timeout: {te}")
        return None
    except ConnectionError as ce:
        logger.error(f"General connection error: {ce}")
        return None
    return client_socket
