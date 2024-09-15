# -*- coding: utf-8 -*-
"""
@date   2024/7/8
@author 2mu
"""

import auto_mysql


if __name__ == '__main__':
    mysql_basename = "/usr/local/mysql-8.0.35"
    mariadb_basename = "/usr/local/mariadb-11.4.2"

    mysql4401 = auto_mysql.MySQL(mysql_basename, 4401)
    if not mysql4401.is_initialized():
        mysql4401.initialize_data_directory('111')
    mysql4401.start()

    spider3306 = auto_mysql.MariaDB(mariadb_basename, 3306)
    if not spider3306.is_initialized():
        spider3306.initialize_data_directory('111')
    spider3306.start()
