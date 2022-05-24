#!/usr/bin/env python
# encoding: utf-8
"""
@file: sniffer.py
@time: 2022/5/23 16:37
@project: black-hat-python-2ed
@desc: P45 简单的原始socket嗅探器，在Windows中需要使用超级管理员启用网卡的混杂模式
"""
import os
import socket

HOST = '172.28.216.90'


def main():
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    # 构建一个socket对象
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((HOST, 0))

    # 设置socket，抓取时包含IP头
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == 'nt':
        # 如果是Windows，运行启用混杂模式
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # 读取一个数据包
    print(sniffer.recvfrom(65565))

    if os.name == 'nt':
        # 关闭网卡的混杂模式
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == '__main__':
    main()
