# -*- coding: utf-8 -*-
"""
生成电话号码相关的字典
"""

# 移动电话前三位, 各自表示三大运营商; (当前忽略物联网卡, 虚拟运行商, 卫星电话卡)
SERVICE_PROVIDER_NUM = [
    # 中国移动
    135, 136, 137, 138, 139, 147, 148, 150, 151, 152,
    157, 158, 159, 178, 182, 183, 184, 187, 188, 195,
    197, 198,
    # 中国联通
    130, 131, 132, 145, 155, 156, 175, 176, 185, 186,
    196,
    # 中国电信
    133, 149, 153, 173, 177, 180, 181, 189, 190, 191,
    193, 199,
    # 中国广电
    192,
]


def generate_phone_num(filename: str) -> bool:
    """
    @brief 生成所有可能的11位电话号码, 如果不按规则, 有10的10次方种可能, 即100亿行数据, 文件非常大....
    所以缩减一些可能性; 号码的1~3位是运营商编号, 4~7位表示归属地, 8~11位没有规则
    @param  filename    写入到指定文件
    @return bool        成功写入指定文件则返回True
    """
    is_success = True
    for provider_num in SERVICE_PROVIDER_NUM:
        assert len(str(provider_num)) == 3
        phone_num = provider_num * 100000000
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                for _ in range(0, 99999999):
                    phone_num += 1
                    buf = f"{phone_num}\n"
                    file.write(buf)
        except Exception as e:
            print(e)
            is_success = False
    return is_success
