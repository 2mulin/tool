# -*- coding: utf-8 -*-
"""
@date   2024/6/10
@author 2mu
"""

import auto_mysql


if __name__ == '__main__':
    # auto_mysql.create_mysql_instance("127.0.0.1", 4401, '2mu', '111')
    # auto_mysql.create_mysql_instance("127.0.0.1", 4402, '2mu', '111')
    # auto_mysql.create_mysql_instance("127.0.0.1", 4403, '2mu', '111')
    auto_mysql.create_mariadb_instance("127.0.0.1", 3306, '2mu', '111')
    auto_mysql.start_mysql_instance("/usr/local/mariadb-11.4.2/bin/mariadbd", "/home/mulin/maria_data/3306/conf/my.cnf")
