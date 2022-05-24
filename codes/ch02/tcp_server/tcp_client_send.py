#!/usr/bin/env python
# encoding: utf-8
"""
@file: tcp_client.py
@time: 2022/5/23 9:55
@project: black-hat-python-2ed
@desc: P13，TCP客户端给服务端发送测试数据包
"""

import socket

target_host = "127.0.0.1"
target_port = 9998

# 创建socket对象
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接客户端
client.connect((target_host, target_port))

# 发送数据
client.send(b"ABCDEF")

# 接收数据
response = client.recv(4096)

print(response.decode())
client.close()
