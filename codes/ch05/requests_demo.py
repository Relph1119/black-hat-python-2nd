#!/usr/bin/env python
# encoding: utf-8
"""
@file: requests_demo.py
@time: 2022/5/24 13:49
@project: black-hat-python-2ed
@desc: P88 requests库的使用
"""

import requests
url = "http://boodelyboo.com"
response = requests.get(url)
print(response.text)


data = {'user': 'tim', 'passwd': '31337'}
response = requests.post(url, data=data)
print(response.text)
