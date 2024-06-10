#-*- coding: utf-8 -*-
"""
@brief 全局变量的声明
相当是配置文件, 可以修改创建实例的MySQL设置; 以及不同的版本;
"""


import logging
import sys


# 在/usr/local/目录下存放了对应的MySQL二进制包, 这里假设已安装mysql-8.0.35
# 如果用户使用包管理工具安装了mysqld, 那就自己修改这里的代码了;
MYSQL_BASENAME = "/usr/local/mysql-8.0.35"
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
mysqlx = OFF # 没用x协议, 就关闭它
mysqlx_port = {port}0
mysqlx_socket = {data_dir}/conf/mysqlx.sock

# 主从复制, MGR中复制相关部件会用到; 即向从节点报告自己的IP,Port
report_host = {ip}
report_port = {port}
"""


# 注意Mariadb和mysql支持的配置是不同的, 有些配置会导致mariadb创建实例失败, 启动失败等情况;
MARIADB_BASENAME = "/usr/local/mariadb-11.4.2"
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


log_handler = logging.StreamHandler(stream=sys.stderr)
log_fotmatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log_handler.setFormatter(log_fotmatter)
log_handler.setLevel(logging.ERROR)

logging.basicConfig(filename='auto_mysql.log', 
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S", 
    encoding='utf-8', level=logging.INFO)
logger = logging.getLogger("auto_mysql")
logger.addHandler(log_handler)
