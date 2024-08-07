# -*- coding: utf-8 -*-
"""
@brief 全局变量的声明
相当是配置文件, 可以修改创建实例的MySQL设置; 以及不同的版本;
"""


import logging
import sys

# 该变量比较关键, 涉及到最后MySQL对外的 report_ip 设置, 必须保证正确;
INTERFACE_NAME = "eth0"

# 如果用户使用包管理工具安装了mysqld, 那就自己修改这里的代码了;
MYSQL_DATA_DIR_TEMPLATE = """/home/{user}/mysql_data/{port}"""
MYSQL_CONF_TEMPLATE = """
[client]
port = {port}
socket = {data_dir}/conf/mysql.sock

[mysqld]
port = {port}
# mysql的安装目录, 很重要, 会影响到安装plugin
basedir = {base_dir}/
datadir = {data_dir}/data
socket = {data_dir}/conf/mysql.sock
pid-file = {data_dir}/conf/mysqld.pid

key_buffer_size = 16M
max_allowed_packet = 128M

log_timestamps = system

general_log = ON
long_query_time = 3
slow_query_log = ON
general_log_file = {data_dir}/log/general.log
log-error = {data_dir}/log/error.log
slow_query_log_file = {data_dir}/log/slow_query.log

# plugin X
mysqlx = OFF
mysqlx_port = {port}0
mysqlx_socket = {data_dir}/conf/mysqlx.sock

# 主从复制, MGR中复制相关部件会用到; 即向从节点报告自己的IP,Port
report_host = {ip}
report_port = {port}
"""


# 注意Mariadb和mysql支持的配置是不同的, 有些配置会导致mariadb创建实例失败, 启动失败等情况;
MARIADB_DATA_DIR_TEMPLATE = """/home/{user}/maria_data/{port}"""
MARIADB_CONF_TEMPLATE = """
[client]
port = {port}
socket = {data_dir}/conf/mysql.sock

[mysqld]
port = {port}
# mariadb的安装目录, 很重要, 会影响到安装plugin
basedir = {base_dir}/
datadir = {data_dir}/data
socket = {data_dir}/conf/mysql.sock
pid-file = {data_dir}/conf/mysqld.pid

key_buffer_size = 16M
max_allowed_packet = 128M

general_log = ON
long_query_time = 3
slow_query_log = ON
general_log_file = {data_dir}/log/general.log
log-error = {data_dir}/log/error.log
slow_query_log_file = {data_dir}/log/slow_query.log

# 主从复制, MGR中复制相关部件会用到; 即向从节点报告自己的IP,Port
report_host = {ip}
report_port = {port}

# 提前增加spider引擎的配置
loose-spider_general_log = ON
"""

# 指定filename参数, 则该函数默认生成一个FileHandler(日志级别是NOTSET)并且加入到root日志记录器
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)d %(message)s",
    filename="auto_mysql.log",                
    datefmt="%Y-%m-%d %H:%M:%S", 
    encoding='utf-8',
    level=logging.INFO)

log_fotmatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)d %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S")
stream_handler = logging.StreamHandler(stream=sys.stderr)
stream_handler.setFormatter(log_fotmatter)
# 控制台只输出ERROR级别以上日志
stream_handler.setLevel(logging.ERROR)
logger = logging.getLogger("root")
logger.addHandler(stream_handler)
