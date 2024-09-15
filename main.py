# -*- coding: utf-8 -*-
"""
@date   2024/7/8
@author 2mu
"""

import auto_mysql


if __name__ == '__main__':
    mysql5_basedir = "/usr/local/mysql-5.5.60"
    mysql8_basedir = "/usr/local/mysql-8.0.35"
    mariadb_basedir = "/usr/local/mariadb-11.4.2"

    mysql5501 = auto_mysql.MySQL5(mysql5_basedir, 5501)
    if not mysql5501.is_initialized():
        mysql5501.initialize_data_directory('111')
    mysql5501.start()

    mysql4401 = auto_mysql.MySQL8(mysql8_basedir, 4401)
    if not mysql4401.is_initialized():
        mysql4401.initialize_data_directory('111')
    mysql4401.start()

    spider3306 = auto_mysql.MariaDB(mariadb_basedir, 3306)
    if not spider3306.is_initialized():
        spider3306.initialize_data_directory('111')
    spider3306.start()
