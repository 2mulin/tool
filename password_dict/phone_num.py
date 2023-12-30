# -*- coding: utf-8 -*-

PHONE_NUM_LEN = 11
# 移动电话前三位, 各自表示三大运营商; (物联网卡, 虚拟运行商, 卫星电话卡忽略...)
SERVICE_PROVIDER_NUM = [
    # 中国移动
    [1,3,5],
    [1,3,6],
    [1,3,7],
    [1,3,8],
    [1,3,9],
    [1,4,7],
    [1,4,8],
    [1,5,0],
    [1,5,1],
    [1,5,2],
    [1,5,7],
    [1,5,8],
    [1,5,9],
    [1,7,8],
    [1,8,2],
    [1,8,3],
    [1,8,4],
    [1,8,7],
    [1,8,8],
    [1,9,5],
    [1,9,7],
    [1,9,8],
    # 中国联通
    [1,3,0],
    [1,3,1],
    [1,3,2],
    [1,4,5],
    [1,4,6],
    [1,5,5],
    [1,5,6],
    [1,7,5],
    [1,7,6],
    [1,8,5],
    [1,8,6],
    [1,9,6],
    # 中国电信
    [1,3,3],
    [1,4,9],
    [1,5,3],
    [1,7,3],
    [1,7,7],
    [1,8,0],
    [1,8,1],
    [1,8,9],
    [1,9,0],
    [1,9,1],
    [1,9,3],
    [1,9,9],
    # 中国广电
    [1,9,2],
]

def _set_phone_num(phone_num_list: list[int], idx: int, file):
    if idx == PHONE_NUM_LEN:
        phone_num: str = ''.join([str(num) for num in phone_num_list])
        file.write(phone_num + '\n')
        return True

    for num in range(0, 10):
        phone_num_list[idx] = num
        _set_phone_num(phone_num_list, idx+1, file)


def generate_phone_num(filename: str) -> bool:
    """
    @brief 生成所有可能的移动电话号码, 10的10次方, 有100亿行数据, 文件非常大....
    所以缩减一些可能性; 号码的1~3位是运营商编号, 4~7位表示归属地;
    @param filename 写入到指定的文件中
    @return bool 成功写入指定文件则返回True
    """
    for provider in SERVICE_PROVIDER_NUM:
        phone_num_list = provider + [0, 0, 0, 0, 0, 0, 0, 0]
        with open(filename, 'w') as file:
            _set_phone_num(phone_num_list, 3, file)
    return True

