# -*- coding: utf-8 -*-
"""
@brief: mysql相关的脚本, 比如支持安装MySQL
@date: 2024/6/2
"""


import os
import platform
import socket
import subprocess
import time
import configparser

import pymysql

from .define import logger
from .define import MYSQL_BASENAME, MYSQL_DATA_DIR_TEMPLATE, MYSQL_CONF_TEMPLATE
from .define import MARIADB_BASENAME, MARIADB_DATA_DIR_TEMPLATE, MARIADB_CONF_TEMPLATE


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


def start_mysql_instance(mysqld: str, my_cnf: str):
    """
    @brief 启动一个mysql实例
    @param mysqld mysqld可执行文件路径
    @param my_cnf mysql实例的配置文件
    """
    if not os.path.exists(mysqld):
        logger.error(f"start mysql instance failed, {mysqld} not exist")
        return False
    if not os.path.exists(my_cnf):
        logger.error(f"start mysql instance failed, {my_cnf} not exist")
        return False
    
    config_parser = configparser.ConfigParser()
    config_parser.read(my_cnf)
    if config_parser.has_section('mysqld') and config_parser.has_option('mysqld', 'port'):
        port = int(config_parser.get('mysqld', 'port'))
    else:
        logger.error(f"The 'mysqld' section or 'port' option does not exist in the {my_cnf}")

    # 设置shell=True, 才能使用&, Linux的shell才支持& 
    command_str = f"nohup {mysqld} --defaults-file={my_cnf} &"
    try:
        complete_proc = subprocess.run(command_str, shell=True, capture_output=True, check=False, encoding='utf-8')
    except Exception as e:
        logger.error(f"start mysql instance failed! {e}")
        return False
    if complete_proc.stdout:
        logger.info(f"{complete_proc.stdout}")
    if complete_proc.returncode or complete_proc.stderr:
        logger.error(f"{complete_proc.stderr}")
        return False

    # 加&后台守护进程启动, 所以需要确保mysql实例启动, 一般启动是很快, 机器负载高的时候可能需要等待...
    count = 0
    success = False
    while not success and count < 10:
        success = is_port_in_use(port)
        time.sleep(2)
        count += 1
    return success


def create_mysql_instance(local_ip: str, port: int, user: str, password: str):
    """
    @brief 创建mysql实例, 数据目录会创建在/home/${USER}/mysql_data/${port}
    @param local_ip 本地机器IP
    @param port     mysql实例开放的端口
    @param user     创建实例后, 新建user
    @param password 创建实例后, root账户和新建user的密码
    """
    # 若是Port已经被监听, 可能导致无法完成实例创建
    if is_port_in_use(port):
        logger.error(f"Port {port} already in use, please confirm")
        return False

    mysqld = f"{MYSQL_BASENAME}/bin/mysqld" 
    if not os.path.exists(mysqld):
        logger.error(f"{MYSQL_BASENAME} not exists! can't create mysql instance")
        return False
    
    username = get_current_username()
    mysql_data_dir = MYSQL_DATA_DIR_TEMPLATE.format(user=username, port=port)
    if os.path.exists(mysql_data_dir):
        logger.error(f"{mysql_data_dir} exists! can't created repeatedly")
        return False
    need_create_dirs = [
        mysql_data_dir,
        f"{mysql_data_dir}/conf",
        f"{mysql_data_dir}/data",
        f"{mysql_data_dir}/log",
    ]
    for dir in need_create_dirs:
        os.makedirs(dir, exist_ok=True)

    try:
        my_cnf = f"{mysql_data_dir}/conf/my.cnf"
        # 将基本的配置写入到my.cnf文件中
        configure_content = MYSQL_CONF_TEMPLATE.format(port=port, data_dir=mysql_data_dir, base_dir=MYSQL_BASENAME,ip=local_ip)
        with open(my_cnf, mode='w', encoding='utf-8') as f:
            f.write(configure_content)
    except Exception as e:
        logger.error(f"{e}")
        return False
    # mysql初始化后root账号是随机密码, 密码输出到错误日志中; 设置--initialize-insecure后则root是空密码
    command_str = f"{mysqld} --defaults-file={my_cnf} --user={username} --initialize-insecure"
    try:
        complete_proc = subprocess.run(command_str.split(), capture_output=True, check=False, encoding='utf-8')
    except Exception as e:
        logger.error(f"{e}")
        return False
    if complete_proc.stdout:
        logger.info(f"{complete_proc.stdout}")
    if complete_proc.returncode or complete_proc.stderr:
        logger.error(f"{complete_proc.stderr}")
        return False
    
    if not start_mysql_instance(mysqld, my_cnf):
        return False
    
    try:
        conn = pymysql.connect(host=local_ip, port=port, user='root')
        cursor = conn.cursor()
        cursor.execute(f"alter user root@'localhost' identified by '{password}'")
        cursor.execute(f"create user {user}@'%' identified by '{password}'")
        # 是否要执行shutdown? 从该函数功能上来说, 只是创建实例, 创建完关闭它没毛病
        # 但是一般创建完, 肯定就是要用的, 那此时就没必要关闭
        cursor.execute("shutdown")
    except Exception as e:
        logger.error(f"{e}")
        return False
    finally:
        cursor.execute("shutdown")
        conn.close()
    return True


def create_mariadb_instance(local_ip: str, port: int, user: str, password: str):
    """
    @brief 创建MariaDB实例, 数据目录会创建在/home/${USER}/maria_data/${port}
    @param local_ip 本地机器IP
    @param port     mysql实例开放的端口
    @param user     创建实例后, 新建user
    @param password 创建实例后, root账户和新建user的密码
    """
    # 若是Port已经被监听, 可能导致无法完成实例创建
    if is_port_in_use(port):
        logger.error(f"Port {port} already in use, please confirm")
        return False

    install_script = f"{MARIADB_BASENAME}/scripts/mariadb-install-db"
    mariadbd = f"{MARIADB_BASENAME}/bin/mariadbd"
    if not os.path.exists(install_script):
        logger.error(f"{MARIADB_BASENAME} not exists! can't create mariadb instance")
        return False
    
    username = get_current_username()
    data_dir = MARIADB_DATA_DIR_TEMPLATE.format(user=username, port=port)
    if os.path.exists(data_dir):
        logger.error(f"{data_dir} exists! can't created repeatedly")
        return False
    need_create_dirs = [
        data_dir,
        f"{data_dir}/conf",
        f"{data_dir}/data",
        f"{data_dir}/log",
    ]
    for dir in need_create_dirs:
        os.makedirs(dir, exist_ok=True)

    try:
        my_cnf = f"{data_dir}/conf/my.cnf"
        # 将基本的配置写入到my.cnf文件中
        configure_content = MARIADB_CONF_TEMPLATE.format(port=port, data_dir=data_dir, base_dir=MARIADB_BASENAME, ip=local_ip)
        with open(my_cnf, mode='w', encoding='utf-8') as f:
            f.write(configure_content)
    except Exception as e:
        logger.error(f"{e}")
        return False
    
    # 初始化数据目录的方法和mysql有区别, 必须用mariadb的指定的shell脚本, 既然是shell脚本, subprocess这里设置shell=True, 并设为True后不能传递命令list, 只能是str 
    command_str = f"{install_script} --defaults-file={my_cnf}" # --user={username}
    try:
        complete_proc = subprocess.run(command_str, shell=True, capture_output=True, check=False, encoding='utf-8')
        # mariadb的初始化脚本写的也不怎么样, 错误都是往stdout输出, 很无语, 导致以下错误捕获实际都没用...
    except Exception as e:
        logger.error(f"{e}")
        return False
    if complete_proc.stdout:
        logger.info(f"{complete_proc.stdout}")
    if complete_proc.returncode or complete_proc.stderr:
        logger.error(f"{complete_proc.stderr}")
        return False
    
    if not start_mysql_instance(mariadbd, my_cnf):
        return False
    
    try:
        # mariadb初始化之后会创建一些奇怪的账号, 暂时不删除它, 后面再看看有什么用, 再决定是否删除
        # 除root@'localhost'之外, 还会创建username@'localhost'账号, 并且也会有所有权限, 但这两初始账号只能通过unix domain socket连接
        conn = pymysql.connect(unix_socket=f'{data_dir}/conf/mysql.sock', user=username)
        cursor = conn.cursor()
        cursor.execute(f"alter user root@'localhost' identified by '{password}'")
        cursor.execute(f"alter user {username}@'localhost' identified by '{password}'")
        cursor.execute(f"create user {user}@'%' identified by '{password}'")
        cursor.execute("select version()")
        version_str: str = cursor.fetchone()[0]
        version = version_str.split('-')[0]
        if version >= "10.4.0":
            cursor.execute("INSTALL SONAME 'ha_spider'")
        else:
            cursor.execute(f"source {MARIADB_BASENAME}/share/install_spider.sql")
    except Exception as e:
        logger.error(f"{e}")
        return False
    finally:
        cursor.execute("shutdown")
        conn.close()
    return True
