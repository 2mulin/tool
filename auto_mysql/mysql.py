# -*- coding: utf-8 -*-


import abc
import os
import signal
import subprocess
import time

import pymysql

from . import util, define
from .define import logger


class MySQLUnix(abc.ABC):
    
    def __init__(self, basedir: str, port: int):
        # mysql安装路径
        self.basedir = basedir
        self.port = port
        self.initialized = False
        self.pid = -1

        self.data_directory = None
        self.mysqld = None
        self.my_cnf = None

    @abc.abstractmethod
    def initialize_data_directory(self, password: str):
        pass

    def is_initialized(self):
        return self.initialized

    def get_version(self):
        """
        @brief 获取MySQL版本号
        """
        command_list = [f"{self.basedir}/bin/mysql_config", "--version"]
        try:
            complete_proc = subprocess.run(command_list, capture_output=True, encoding='utf-8')
        except Exception as e:
            logger.error(f"{e}")
            return None
        if complete_proc.returncode or complete_proc.stderr:
            logger.error(f"get mysql version failed! {complete_proc.stderr}")
            return None
        # 去除换行符
        return complete_proc.stdout.strip()

    def get_pid(self):
        """
        @brief 获取mysqld进程pid, -1表示进程未启动
        """
        pid_file = f"{self.data_directory}/run/mysqld.pid"
        if os.path.exists(pid_file):
            with open(pid_file, mode='r') as f:
                self.pid = int(f.readline())
        return self.pid

    def is_started(self):
        """
        @brief 判断mysql服务是否已经启动
        """
        self.get_pid()
        if self.pid == -1:
            return False
        if not os.path.exists(f"/proc/{self.pid}"):
            self.pid = -1
            return False
        if not util.is_port_in_use(self.port):
            return False
        return True

    def start(self):
        """
        @brief 启动mysql服务, 不要重复启动... 否则mysqld进程真可以开多个
        """
        if self.is_started():
            return True

        check_list= [self.mysqld, self.data_directory, self.my_cnf]
        for check in check_list:
            if not os.path.exists(check):
                logger.error(f"start mysql instance failed, {check} not exist")
                return False
        
        # 设置shell=True才使用Linux的shell去执行指令, 才能使用& 后台启动
        command_str = f"nohup {self.mysqld} --defaults-file={self.my_cnf} &"
        try:
            complete_proc = subprocess.run(command_str, shell=True,
                                           capture_output=True, encoding='utf-8')
        except Exception as e:
            logger.error(f"start mysql instance failed! {e}")
            return False
        if complete_proc.stdout:
            logger.info(f"{complete_proc.stdout}")
        # 有stderr不代表启动失败, 因为mysql 5.5.60启动warning, node日志都会往stderr中输出, 但实际上会启动是成功的;
        if complete_proc.stderr:
            logger.error(f"stderr log <\n{complete_proc.stderr}>")
        if complete_proc.returncode:
            logger.error(f"start mysql instance failed! {complete_proc.stderr}")
            return False

        # 需要确保mysql实例启动, 通常启动非常快, 但机器负载高的时候可能需要等待...
        for _ in range(10):
            if util.is_port_in_use(self.port):
                return True
            time.sleep(2)
        return False

    def stop(self):
        """
        @brief 关闭mysql服务;
        """
        if not self.is_started():
            return True
        os.kill(self.pid, signal.SIGQUIT)
        for _ in range(10):
            if os.path.exists(f"/proc/{self.pid}"):
                time.sleep(2)
            else:
                return True
        return False
    
    def create_replicate_user(self, root_password, replicate_user, replicate_password):
        """
        @brief 创建用于主从复制的账号
        """
        try:
            conn = pymysql.connect(host="127.0.0.1", port=self.port, 
                                   user='root', password=root_password)
            cursor = conn.cursor()
            cursor.execute(f"create user {replicate_user}@'%' identified by '{replicate_password}'")
            cursor.execute(f"grant replication slave on *.* to '{replicate_user}'@'%' ")
        except Exception as e:
            logger.error(f"create replicate user failed: {e}")
            return False
        return True

    def change_master(self, root_password, master_host, master_port, 
                      replicate_user, replicate_password,
                      binlog_file = None, binlog_pos = None):
        """
        @brief 以当前节点为从节点, 设置主从复制通道;
        @param root_password 从节点场超级管理员账号的密码
        @param master_host 主节点IP
        @param master_port 主节点Port
        @param replicate_user 主节点复制账号名
        @param replicate_password 主节点复制账号的密码
        """
        sql = (f"change master to master_host='{master_host}', master_port={master_port}, "
               f"master_user='{replicate_user}', master_password='{replicate_password}'")
        if binlog_file and binlog_pos:
            sql = f"{sql}, master_log_file='{binlog_file}', master_log_pos='{binlog_pos}'"
        try:
            conn = pymysql.connect(host="127.0.0.1", port=self.port,
                                user="root", password=root_password)
            cursor = conn.cursor()
            cursor.execute(sql)
            cursor.execute(f"start slave")
        except Exception as e:
            logger.error(f"set replicate failed: {e}")
            return False
        return True



class MySQL5(MySQLUnix):

    def __init__(self, basename: str, port: int):
        super().__init__(basename, port)
        username = util.get_current_username()
        self.data_directory = define.MYSQL5_DATA_DIR_TEMPLATE.format(user=username, port=port)
        if os.path.exists(self.data_directory):
            self.initialized = True

        self.mysqld = f"{self.basedir}/bin/mysqld"
        self.my_cnf = f"{self.data_directory}/conf/my.cnf"

    def initialize_data_directory(self, password: str):
        """
        @brief 创建mysql实例, 数据目录都会创建在/home/${USER}/mysql_data/${PORT};
        mysql5和mysql8初始化方式不同, 所以单独开个类来实现;
        @param password  创建实例后, 修改root账户的密码
        """
        if util.is_port_in_use(self.port):
            logger.error(f"Port {self.port} already in use, can't create mysql instance, please confirm")
            return False
         
        if not os.path.exists(self.mysqld):
            logger.error(f"{self.mysqld} not exists! can't create mysql instance")
            return False
        
        username = util.get_current_username()
        if os.path.exists(self.data_directory):
            logger.error(f"{self.data_directory} exists! can't created repeatedly")
            return False
        need_create_dirs = [
            self.data_directory,
            f"{self.data_directory}/conf",
            f"{self.data_directory}/run",
            f"{self.data_directory}/data",
            f"{self.data_directory}/log",
        ]
        for dir in need_create_dirs:
            os.makedirs(dir, exist_ok=True)
        
        local_ip = util.get_ip_address(define.INTERFACE_NAME)
        my_cnf_content = define.MYSQL5_CONF_TEMPLATE.format(base_dir=self.basedir,
                                                           data_dir=self.data_directory,
                                                           ip=local_ip, port=self.port)
        # 将基本的配置写入到my.cnf文件中
        try:
            with open(self.my_cnf, mode='w', encoding='utf-8') as f:
                f.write(my_cnf_content)
        except Exception as e:
            logger.error(f"{e}")
            return False
        # 主要就是以下部分开始有区别, 还必须直接指定basedir才能创建成功, self.my_cnf指定的还不生效...
        command = [f"{self.basedir}/scripts/mysql_install_db",
                   f"--basedir={self.basedir}",
                   f"--defaults-file={self.my_cnf}",
                   f"--user={username}"]
        try:
            complete_proc = subprocess.run(command, capture_output=True, encoding='utf-8')
        except Exception as e:
            logger.error(f"{e}")
            return False
        if complete_proc.stdout:
            logger.info(f"{complete_proc.stdout}")
        if complete_proc.stderr:
            logger.error(f"mysql5 log <\n{complete_proc.stderr}>")
        if complete_proc.returncode:
            logger.error(f"mysql5 initialize data directory failed!")
            return False
        
        if not self.start():
            return False
        
        try:
            conn = pymysql.connect(host="127.0.0.1", port=self.port, user='root')
            cursor = conn.cursor()
            # 修改密码的SQL也不同...
            cursor.execute(f"set password for root@'localhost' = password('{password}')")
        except Exception as e:
            logger.error(f"{e}")
            return False
        self.initialized = True
        return True


class MySQL8(MySQLUnix):

    def __init__(self, basename: str, port: int):
        super().__init__(basename, port)
        username = util.get_current_username()
        self.data_directory = define.MYSQL8_DATA_DIR_TEMPLATE.format(user=username, port=port)
        if os.path.exists(self.data_directory):
            self.initialized = True

        self.mysqld = f"{self.basedir}/bin/mysqld"
        self.my_cnf = f"{self.data_directory}/conf/my.cnf"

    def initialize_data_directory(self, password: str):
        """
        @brief 创建mysql实例, 数据目录都会创建在/home/${USER}/mysql_data/${port}
        @param password  创建实例后, 修改root账户的密码
        """
        if util.is_port_in_use(self.port):
            logger.error(f"Port {self.port} already in use, can't create mysql instance, please confirm")
            return False
         
        if not os.path.exists(self.mysqld):
            logger.error(f"{self.mysqld} not exists! can't create mysql instance")
            return False
        
        username = util.get_current_username()
        if os.path.exists(self.data_directory):
            logger.error(f"{self.data_directory} exists! can't created repeatedly")
            return False
        need_create_dirs = [
            self.data_directory,
            f"{self.data_directory}/conf",
            f"{self.data_directory}/run",
            f"{self.data_directory}/data",
            f"{self.data_directory}/log",
        ]
        for dir in need_create_dirs:
            os.makedirs(dir, exist_ok=True)
        
        local_ip = util.get_ip_address(define.INTERFACE_NAME)
        my_cnf_content = define.MYSQL8_CONF_TEMPLATE.format(base_dir=self.basedir,
                                                           data_dir=self.data_directory,
                                                           ip=local_ip, port=self.port)
        # 将基本的配置写入到my.cnf文件中
        try:
            with open(self.my_cnf, mode='w', encoding='utf-8') as f:
                f.write(my_cnf_content)
        except Exception as e:
            logger.error(f"{e}")
            return False
        # mysql初始化后root账号是随机密码, 密码输出到错误日志中; 设置--initialize-insecure后则root是空密码
        command_str = f"{self.mysqld} --defaults-file={self.my_cnf} --user={username} --initialize-insecure"
        try:
            complete_proc = subprocess.run(command_str.split(), capture_output=True, encoding='utf-8')
        except Exception as e:
            logger.error(f"{e}")
            return False
        if complete_proc.stdout:
            logger.info(f"{complete_proc.stdout}")
        if complete_proc.returncode or complete_proc.stderr:
            logger.error(f"{complete_proc.stderr}")
            return False
        
        if not self.start():
            return False
        
        try:
            conn = pymysql.connect(host="127.0.0.1", port=self.port, user='root')
            cursor = conn.cursor()
            cursor.execute(f"alter user root@'localhost' identified by '{password}'")
        except Exception as e:
            logger.error(f"{e}")
            return False
        self.initialized = True
        return True
    

class MariaDB(MySQLUnix):

    def __init__(self, basename: str, port: int):
        super().__init__(basename, port)
        username = util.get_current_username()
        self.data_directory = define.MARIADB_DATA_DIR_TEMPLATE.format(user=username, port=port)
        if os.path.exists(self.data_directory):
            self.initialized = True

        # 虽然mysqld也可以使用, 但是会有告警...
        self.mysqld = f"{self.basedir}/bin/mariadbd"
        self.my_cnf = f"{self.data_directory}/conf/my.cnf"

    def initialize_data_directory(self, password: str):
        """
        @brief 创建MariaDB实例, 数据目录会创建在/home/${USER}/maria_data/${port}
        @param password  创建实例后, root账户和新建user的密码
        """
        # 若是Port已经被监听, 则无法完成实例创建
        if util.is_port_in_use(self.port):
            logger.error(f"Port {self.port} already in use, please confirm")
            return False

        install_script = f"{self.basedir}/scripts/mariadb-install-db"
        mariadbd = f"{self.basedir}/bin/mariadbd"
        if not os.path.exists(install_script):
            logger.error(f"{self.basedir} not exists! can't create mariadb instance")
            return False
        
        username = util.get_current_username()
        data_directory = define.MARIADB_DATA_DIR_TEMPLATE.format(user=username, port=self.port)
        if os.path.exists(data_directory):
            logger.error(f"{data_directory} exists! can't created repeatedly")
            return False
        need_create_dirs = [
            data_directory,
            f"{data_directory}/conf",
            f"{data_directory}/run",
            f"{data_directory}/data",
            f"{data_directory}/log",
        ]
        for dir in need_create_dirs:
            os.makedirs(dir, exist_ok=True)
        
        local_ip = util.get_ip_address(define.INTERFACE_NAME)
        my_cnf_content = define.MARIADB_CONF_TEMPLATE.format(base_dir=self.basedir,
                                                                data_dir=self.data_directory,
                                                                ip=local_ip, port=self.port)
        # 将基本的配置写入到my.cnf文件中
        try:
            with open(self.my_cnf, mode='w', encoding='utf-8') as f:
                f.write(my_cnf_content)
        except Exception as e:
            logger.error(f"{e}")
            return False
        
        # 初始化数据目录的方法和mysql有区别, 必须用mariadb的指定的shell脚本;
        # 既然是shell脚本, subprocess这里设置shell=True, 并设为True后不能传递命令list, 只能是str 
        command_str = f"{install_script} --defaults-file={self.my_cnf}"
        try:
            complete_proc = subprocess.run(command_str, shell=True, 
                                           capture_output=True, encoding='utf-8')
        except Exception as e:
            logger.error(f"{e}")
            return False
        if complete_proc.stdout:
            logger.info(f"initialize data directory failed: {complete_proc.stdout}")
        if complete_proc.returncode or complete_proc.stderr:
            logger.error(f"initialize data directory failed: {complete_proc.stderr}")
            return False
        
        if not self.start():
            return False
        
        version = self.get_version()
        
        # mariadb初始化之后会创建一些奇怪的账号, 暂时不删除它, 后面再看看有什么用, 再决定是否删除
        # 除root@'localhost'之外, 还会创建username@'localhost'账号, 并且也会有所有权限, 但这两初始账号只能通过unix domain socket连接
        unix_sock = f'{data_directory}/run/mysql.sock'
        try:
            conn = pymysql.connect(unix_socket=unix_sock, user=username)
            cursor = conn.cursor()
            cursor.execute(f"alter user root@'localhost' identified by '{password}'")
            cursor.execute(f"alter user {username}@'localhost' identified by '{password}'")

            # 10.4.0以上版本安装非常简单
            if util.compare_version("10.4.0", version) <= 0:
                cursor.execute("INSTALL SONAME 'ha_spider'")
            else:
                # 通过mysql api无法无法执行 source 指令，只能通过mysql client执行source指令...
                command_list = [f"{self.basedir}/bin/mysql", 
                                f"--socket={unix_sock}"
                                "-s",
                                f"-e 'source {self.basedir}/share/install_spider.sql'"]
                subprocess.run(command_list, capture_output=True, encoding='utf-8')
        except Exception as e:
            logger.error(f"install spider engine failed: {e}")
            return False
        self.initialized = True
        return True
