#!/usr/bin/env python
# encoding: utf-8
"""
@file: ssh_cmd.py.py
@time: 2022/5/23 15:39
@project: black-hat-python-2ed
@desc: P30 基于Paramiko的SSH通信
"""
import getpass

import paramiko


def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print("--- Output ---")
        for line in output:
            print(line.strip())


if __name__ == '__main__':
    user = input('Username: ')
    password = getpass.getpass()
    ip = input('Enter server IP: ') or '192.168.56.101'
    port = input('Enter port or <CR>: ') or 2222
    cmd = input('Enter command or <CR>: ') or 'id'
    ssh_command(ip, port, user, password, cmd)
