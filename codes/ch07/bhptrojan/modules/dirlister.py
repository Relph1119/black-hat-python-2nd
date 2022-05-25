#!/usr/bin/env python
# encoding: utf-8
"""
@file: dirlister.py
@time: 2022/5/25 11:38
@project: black-hat-python-2ed
@desc: P141 遍历文件目录
"""
import os


def run(**args):
    print("[*] In dirlister module.")
    files = os.listdir(".")
    return str(files)
