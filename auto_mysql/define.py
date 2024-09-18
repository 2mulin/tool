# -*- coding: utf-8 -*-
"""
@brief 全局变量的声明
相当是配置文件, 可以修改创建实例的MySQL设置; 以及不同的版本;
"""


import logging
import sys

# 该变量涉及到最后MySQL对外暴露的 report_ip 变量, 影响主从复制, 必须保证正确;
INTERFACE_NAME = "eth0"


MYSQL5_DATA_DIR_TEMPLATE = """/home/{user}/mysql5_data/{port}"""
MYSQL5_CONF_TEMPLATE = """
[client]
port = {port}
socket = {data_dir}/run/mysql.sock

[mysqld]
# mysql的安装目录, 很重要, 会影响到安装plugin
basedir = {base_dir}/
datadir = {data_dir}/data
port = {port}

# mysqld运行过程中会生成的文件
socket = {data_dir}/run/mysql.sock
pid-file = {data_dir}/run/mysqld.pid

# secure_file_priv 这个变量被用于限制导入和导出的数据目录;
# 比如 LOAD DATA 和 SELECT ... INTO OUTFILE 语句, 以及 LOAD_FILE() 函数;
# 限制到每个实例的run目录, 默认情况或不设置都有告警...
secure_file_priv = {data_dir}/run/

key_buffer_size = 16M
max_allowed_packet = 128M

# 默认OFF, 不然初始化数据目录会有很多日志
general_log = OFF
long_query_time = 3
slow_query_log = ON
general_log_file = {data_dir}/log/general.log
log-error = {data_dir}/log/error.log
slow_query_log_file = {data_dir}/log/slow_query.log

# 默认OFF, 必须自己设置
log_bin = ON
server_id = {port}

# 主从复制和MGR会使用到; 这两个变量的作用是向从节点报告自己的IP, Port
report_host = {ip}
report_port = {port}
"""


MYSQL8_DATA_DIR_TEMPLATE = """/home/{user}/mysql8_data/{port}"""
MYSQL8_CONF_TEMPLATE = """
[client]
port = {port}
socket = {data_dir}/run/mysql.sock

[mysqld]
# mysql的安装目录, 很重要, 会影响到安装plugin
basedir = {base_dir}/
datadir = {data_dir}/data
port = {port}

# mysqld运行过程中会生成的文件
socket = {data_dir}/run/mysql.sock
pid-file = {data_dir}/run/mysqld.pid

key_buffer_size = 16M
max_allowed_packet = 128M

log_timestamps = system

# 默认OFF, 不然初始化数据目录会有很多日志
general_log = OFF
long_query_time = 3
slow_query_log = ON
general_log_file = {data_dir}/log/general.log
log-error = {data_dir}/log/error.log
slow_query_log_file = {data_dir}/log/slow_query.log

# plugin X
mysqlx = OFF
mysqlx_port = {port}0
mysqlx_socket = {data_dir}/conf/mysqlx.sock

log_bin = ON
server_id = {port}

# 主从复制和MGR会使用到; 这两个变量的作用是向从节点报告自己的IP, Port
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
# mariadb的安装目录, 很重要, 会影响到安装plugin
basedir = {base_dir}/
datadir = {data_dir}/data
port = {port}

# mysqld运行过程中会生成的文件
socket = {data_dir}/run/mysql.sock
pid-file = {data_dir}/run/mysqld.pid

key_buffer_size = 16M
max_allowed_packet = 128M

# 默认OFF, 不然初始化数据目录会有很多日志
general_log = OFF
long_query_time = 3
slow_query_log = ON
general_log_file = {data_dir}/log/general.log
log-error = {data_dir}/log/error.log
slow_query_log_file = {data_dir}/log/slow_query.log

# 主从复制, MGR中复制相关部件会用到; 即向从节点报告自己的IP,Port
report_host = {ip}
report_port = {port}

log_bin = ON
server_id = {port}

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
