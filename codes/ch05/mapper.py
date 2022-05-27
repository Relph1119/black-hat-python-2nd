#!/usr/bin/env python
# encoding: utf-8
"""
@file: mapper.py
@time: 2022/5/24 14:10
@project: black-hat-python-2ed
@desc: P92 拓印WordPress系统结构
"""
import contextlib
import os
import queue


import sys
import threading
import time

import requests

# 设定不想扫描的文件扩展名列表
FILTERED = [".jpg", ".gif", ".png", ".css"]
# 设置远程目标的网址
TARGET = "http://192.168.56.101/wordpress"
THREADS = 10

answers = queue.Queue()
# 存储准备扫描的路径
web_paths = queue.Queue()


def gather_paths():
    # 扫描本地Web应用安装目录里的所有文件和目录
    for root, _, files in os.walk('.'):
        for fname in files:
            if os.path.splitext(fname)[1] in FILTERED:
                continue
            path = os.path.join(root, fname)
            if path.startswith('.'):
                path = path[1:]
            print(path)
            web_paths.put(path)


@contextlib.contextmanager
def chdir(path):
    this_dir = os.getcwd()
    os.chdir(path)
    try:
        # 将控制权转移给gather_paths()
        yield
    finally:
        # 回到原本的目录
        os.chdir(this_dir)


def test_remote():
    """
    检测路径是否可以访问
    :return:
    """
    while not web_paths.empty():
        path = web_paths.get()
        url = f"{TARGET}{path}"
        time.sleep(2)
        r = requests.get(url)
        if r.status_code == 200:
            answers.put(url)
            sys.stdout.write("+")
        else:
            sys.stdout.write("x")
        sys.stdout.flush()


def run():
    mythreads = list()
    for i in range(THREADS):
        print(f"Spawning thread {i}")
        t = threading.Thread(target=test_remote)
        mythreads.append(t)
        t.start()

    for thread in mythreads:
        thread.join()


if __name__ == '__main__':
    with chdir("./wordpress"):
        gather_paths()
    input('Press return to continue.')

    run()
    with open('./myanswres.txt', 'w') as f:
        while not answers.empty():
            f.write(f"{answers.get()}\n")

    print("done")
