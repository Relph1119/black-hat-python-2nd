#!/usr/bin/env python
# encoding: utf-8
"""
@file: environment.py
@time: 2022/5/25 11:40
@project: black-hat-python-2ed
@desc: P142 收集远程设备上设定的所有环境变量
"""
import os


def run(**args):
    print("[*] In environment module.")
    return os.environ