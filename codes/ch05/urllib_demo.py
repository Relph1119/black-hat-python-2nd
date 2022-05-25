#!/usr/bin/env python
# encoding: utf-8
"""
@file: urllib_demo.py
@time: 2022/5/24 11:47
@project: black-hat-python-2ed
@desc: P88 urllib库的使用
"""
import urllib.request

url = "http://boodelyboo.com"
with urllib.request.urlopen(url) as response:
    content = response.read()

print(content)

info = {'user': 'tim', 'passwd': '31337'}
data = urllib.parse.urlencode(info).encode()

req = urllib.request.Request(url, data)
with urllib.request.urlopen(req) as response:
    content = response.read()

print(content)