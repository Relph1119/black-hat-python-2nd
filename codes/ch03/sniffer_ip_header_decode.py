#!/usr/bin/env python
# encoding: utf-8
"""
@file: sniffer_ip_header_decode.py
@time: 2022/5/23 19:20
@project: black-hat-python-2ed
@desc: P53 IP解码器，在Windows环境中使用系统管理员运行
"""
import ipaddress
import os
import socket
import struct
import sys


class IP:
    def __init__(self, buff=None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)
        # 版本
        self.ver = header[0] >> 4
        # 头长度
        self.ihl = header[0] & 0xF
        # 服务类型
        self.tos = header[1]
        # 总长度
        self.len = header[2]
        # 标识
        self.id = header[3]
        # 段偏移
        self.offset = header[4]
        # 生存时间
        self.ttl = header[5]
        # 协议
        self.protocol_num = header[6]
        # 头校验和
        self.sum = header[7]
        # 源IP地址
        self.src = header[8]
        # 目的IP地址
        self.dst = header[9]

        # 转换成IP地址的可读形式
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            print("%s No protocol for %s" % (e, self.protocol_num))
            self.protocol = str(self.protocol_num)


def sniff(host):
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))
    # 设置socket，抓取时包含IP头
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == "nt":
        # 如果是Windows，运行启用混杂模式
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            # 读取一个数据包
            raw_buffer = sniffer.recvfrom(65535)[0]
            # 将前20字节转换成IP头对象
            ip_header = IP(raw_buffer[0:20])
            print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))
    except KeyboardInterrupt:
        if os.name == "nt":
            # 关闭网卡的混杂模式
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = "172.28.216.90"
    sniff(host)
