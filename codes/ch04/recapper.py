#!/usr/bin/env python
# encoding: utf-8
"""
@file: recapper.py
@time: 2022/5/24 10:05
@project: black-hat-python-2ed
@desc: P76 pcap文件处理
"""
import collections
import os

# 设置保存图片的目录
import re
import sys
import zlib

from scapy.layers.inet import TCP
from scapy.utils import rdpcap

OUTPUT = "/root/Desktop/pictures"
# 设置pcap文件路径
PCAPS = "/root/Downloads"

# 定义Response命名元组
Response = collections.namedtuple('Response', ['header', 'payload'])


def get_header(payload):
    """
    获取数据包头
    :param payload:
    :return:
    """
    try:
        # 提取HTTP头
        header_raw = payload[:payload.index(b'\r\n\r\n') + 2]
    except ValueError:
        sys.stdout.write("-")
        sys.stdout.flush()
        return None

    # 把HTTP头的每一行进行分割成字段名:字段值
    header = dict(re.findall(r'(?P<name>.*?):(?P<value>.*?)\r\n', header_raw.decode()))
    if "Content-Type" not in header:
        return None
    return header


def extract_content(Response, content_name='image'):
    """
    提取数据包内容
    :param Response:
    :param content_name:
    :return:
    """
    content, content_type = None, None
    if content_name in Response.header['Content-Type']:
        # 将数据头指定的实际数据类型保存下来
        content_type = Response.header['Content-Type'].split('/')[1]
        # 保存payload中HTTP头之后的全部数据
        content = Response.payload[Response.payload.index(b'\r\n\r\n') + 4]

        if "Content-Encoding" in Response.header:
            # 进行图片解压
            if Response.header["Content-Encoding"] == "gzip":
                content = zlib.decompress(Response.payload, zlib.MAX_WBITS | 32)
            elif Response.header["Content-Encoding"] == "deflate":
                content = zlib.decompress(Response.payload)

    return content, content_type


class Recapper:
    def __init__(self, fname):
        pcap = rdpcap(fname)
        # 自动切分每个TCP会话
        self.sessions = pcap.sessions()
        self.responses = list()

    def get_responses(self):
        """
        负责从pcap文件中读取响应数据
        :return:
        """
        # 遍历所有会话
        for session in self.sessions:
            payload = b''
            # 遍历所有数据包
            for packet in self.sessions[session]:
                try:
                    # 只处理发往80端口或从80端口接收的数据
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                        payload += bytes(packet[TCP].payload)
                except IndexError:
                    # 如果没有成功拼接payload缓冲区，在屏幕上打印一个x
                    sys.stdout.write('x')
                    sys.stdout.flush()
            if payload:
                # 检查HTTP头的内容
                header = get_header(payload)
                if header is None:
                    continue
                self.responses.append(Response(header=header, payload=payload))

    def write(self, content_name):
        """
        把响应数据中的图片写到输出目录下
        :param content_name:
        :return:
        """
        for i, response in enumerate(self.responses):
            # 提取响应内容
            content, content_type = extract_content(response, content_name)
            if content and content_type:
                fname = os.path.join(OUTPUT, f'ex_{i}.{content_type}')
                print(f'Writing {fname}')
                # 写入文件中
                with open(fname, "wb") as f:
                    f.write(content)


if __name__ == '__main__':
    pfile = os.path.join(PCAPS, 'pcap.pcap')
    recapper = Recapper(pfile)
    recapper.get_responses()
    recapper.write('image')
