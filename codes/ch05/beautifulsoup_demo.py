#!/usr/bin/env python
# encoding: utf-8
"""
@file: beautifulsoup_demo.py
@time: 2022/5/24 14:05
@project: black-hat-python-2ed
@desc: P90 BeautifulSoup库的使用
"""
import requests
from bs4 import BeautifulSoup as bs

url = "https://bing.com"
r = requests.get(url)
tree = bs(r.text, 'html.parser')
for link in tree.find_all('a'):
    print(f"{link.get('href')} -> {link.text}")