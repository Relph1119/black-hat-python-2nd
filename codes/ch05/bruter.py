#!/usr/bin/env python
# encoding: utf-8
"""
@author: HuRuiFeng
@file: bruter.py
@time: 2022/5/24 16:02
@project: black-hat-python-2ed
@desc: P99 暴力破解目录和文件位置
"""
import queue
import sys
import threading

import requests.exceptions

AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
EXTENSIONS = ['.php', '.bak', '.orig', '.inc']
TARGET = "http://testphp.vulnweb.com"
THREAD = 50
WORDLIST = "./svn_digger/all.txt"


def get_words(resume=None):
    def extentd_words(word):
        if "." in word:
            words.put(f"/{word}")
        else:
            words.put(f"/{word}/")

        for extension in EXTENSIONS:
            words.put(f"/{word}/{extension}")

    # 读取暴破字典文件
    with open(WORDLIST) as f:
        raw_words = f.read()

    found_resume = False
    words = queue.Queue()
    for word in raw_words.split():
        # 设置成上一次扫描到的最后路径
        if resume is not None:
            if found_resume:
                extentd_words(word)
            elif word == resume:
                found_resume = True
                print(f"Resuming wordlist from: {resume}")
        else:
            print(word)
            extentd_words(word)
    # 得到待扫描的路径
    return words


def dir_bruter(words):
    headers = {'User-Agent': AGENT}
    while not words.empty():
        # 生成远程目标的URL
        url = f"{TARGET}{words.get()}"
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            sys.stderr.write("x")
            sys.stderr.flush()
            continue

        if r.status_code == 200:
            print(f"\nSuccess ({r.status_code}: {url})")
        elif r.status_code == 404:
            sys.stderr.write(".")
            sys.stderr.flush()
        else:
            print(f"{r.status_code} => {url}")


if __name__ == '__main__':
    words = get_words()
    print("Press return to continue.")
    sys.stdin.readline()
    for _ in range(THREAD):
        t = threading.Thread(target=dir_bruter, args=(words,))
        t.start()
