# -*- coding: utf-8 -*-
"""
@date   2024/9/17
@author 2mu
@brief  入口
"""

import auto_mysql


def startMariadb(port):
    mariadb_basedir = "/usr/local/mariadb-11.4.2"
    mariadb = auto_mysql.MariaDB(mariadb_basedir, port)
    if not mariadb.is_initialized():
        mariadb.initialize_data_directory('111')
    mariadb.start()
    return mariadb


def startMySQL5(port):
    mysql5_basedir = "/usr/local/mysql-5.5.60"
    mysql_instance = auto_mysql.MySQL5(mysql5_basedir, port)
    if not mysql_instance.is_initialized():
        mysql_instance.initialize_data_directory('111')
    mysql_instance.start()
    return mysql_instance


def startMySQL8(port):
    mysql8_basedir = "/usr/local/mysql-8.0.35"
    mysql_instance = auto_mysql.MySQL8(mysql8_basedir, port)
    if not mysql_instance.is_initialized():
        mysql_instance.initialize_data_directory('111')
    mysql_instance.start()
    return mysql_instance


if __name__ == '__main__':
    instance_5501 = startMySQL5(5501)
    instance_5502 = startMySQL5(5502)
    # 设置主从复制
    instance_5501.create_replicate_user('111', 'repl', '111')
    # ubuntu不能使用127.0.0.1连接mysql, 127.0.0.1会先匹配localhost, 但是repl@localhost账号不存在, 所以连接不上...
    instance_5502.change_master('111', '127.0.0.1', '5501', 'repl', '111')
    