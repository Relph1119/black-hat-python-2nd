#!/usr/bin/env python
# encoding: utf-8
"""
@file: tcp_client.py
@time: 2022/5/23 9:55
@project: black-hat-python-2ed
@desc: P10，TCP客户端
"""

import socket

target_host = "www.baidu.com"
target_port = 80

# 创建socket对象
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接客户端
client.connect((target_host, target_port))

# 发送数据
client.send(b"GET / HTTP/1.1\r\nHost: baidu.com\r\n\r\n")

# 接收数据
response = client.recv(4096)

print(response.decode())
client.close()
