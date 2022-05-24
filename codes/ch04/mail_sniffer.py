#!/usr/bin/env python
# encoding: utf-8
"""
@file: mail_sniffer.py
@time: 2022/5/23 20:36
@project: black-hat-python-2ed
@desc: P64 嗅探邮箱协议
"""
from scapy.sendrecv import sniff


def packet_callback(packet):
    print(packet.show())


def main():
    # 嗅探所有网卡，不带任何过滤条件
    sniff(prn=packet_callback, count=1)


if __name__ == '__main__':
    main()
