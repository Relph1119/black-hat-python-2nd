#!/usr/bin/env python
# encoding: utf-8
"""
@file: scanner.py
@time: 2022/5/23 20:03
@project: black-hat-python-2ed
@desc: P58 在整个子网进行主机扫描
在Windows环境中使用系统管理员运行
"""
import ipaddress
import os
import socket
import struct
import sys
import threading
import time

SUBNET = "172.28.0.0/16"

# 定义签名，用于确认收到的ICMP响应是由发送的UDP包所触发的
MESSAGE = 'PYTHONRULES!'


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


class ICMP:
    def __init__(self, buff):
        header = struct.unpack('<BBHHH', buff)
        # 类型
        self.type = header[0]
        # 代码
        self.code = header[1]
        # 头校验和
        self.sum = header[2]
        # 标识
        self.id = header[3]
        # 请求
        self.seq = header[4]


def udp_sender():
    """
    读取子网地址，并往这个子网的每个IP地址发送UDP数据包
    :return:
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            sender.sendto(bytes(MESSAGE, 'utf8'), (str(ip), 65212))


class Scanner:
    def __init__(self, host):
        self.host = host
        if os.name == "nt":
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        self.socket.bind((host, 0))
        # 设置socket，抓取时包含IP头
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name == "nt":
            # 如果是Windows，运行启用混杂模式
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def sniff(self):
        hosts_up = {f"{str(self.host)} *"}
        try:
            while True:
                # 读取一个数据包
                raw_buffer = self.socket.recvfrom(65535)[0]
                # 将前20字节转换成IP头对象
                ip_header = IP(raw_buffer[0:20])
                if ip_header.protocol == "ICMP":
                    # 计算ICMP数据在原始数据包中的编译
                    offset = ip_header.ihl * 4
                    buf = raw_buffer[offset:offset + 8]

                    # 按照ICMP结构进行解析
                    icmp_header = ICMP(buf)
                    # 判断目标不可达，端口不可达
                    if icmp_header.code == 3 and icmp_header.type == 3:
                        # 检查这个响应是否来自我们正在扫描的子网
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Network(SUBNET):
                            # 检查ICMP消息是否有自定义的签名
                            if raw_buffer[len(raw_buffer) - len(MESSAGE):] == bytes(MESSAGE, 'utf8'):
                                tgt = str(ip_header.src_address)
                                if tgt != self.host and tgt not in hosts_up:
                                    hosts_up.add(str(ip_header.src_address))
                                    print(f"Host Up: {tgt}")
        except KeyboardInterrupt:
            if os.name == "nt":
                # 关闭网卡的混杂模式
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

            print('\nUser interrupted.')
            if hosts_up:
                print(f"\n\nSummary: Hosts up on {SUBNET}")
            for host in sorted(hosts_up):
                print(f"{host}")
            print("")
            sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = "172.28.216.90"
    s = Scanner(host)
    time.sleep(5)
    # 先为udp_sender开启一个独立线程，以免干扰嗅探的效果
    t = threading.Thread(target=udp_sender)
    t.start()
    s.sniff()
