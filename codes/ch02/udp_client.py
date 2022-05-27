#!/usr/bin/env python
# encoding: utf-8
"""
@file: udp_client.py
@time: 2022/5/23 9:59
@project: black-hat-python-2ed
@desc: P11 UDP客户端
"""

import socket

target_host = "127.0.0.1"
target_ip = 9997

# 创建socket对象
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 发送数据
client.sendto(b"AAABBBCCC", (target_host, target_ip))

# 接收数据
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()
