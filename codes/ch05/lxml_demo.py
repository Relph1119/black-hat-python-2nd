#!/usr/bin/env python
# encoding: utf-8
"""
@file: lxml_demo.py
@time: 2022/5/24 13:59
@project: black-hat-python-2ed
@desc: P89 lxml库的使用
"""
import requests
from lxml import etree
from io import BytesIO

url = "https://nostarch.com"
r = requests.get(url)
content = r.content

parser = etree.HTMLParser()
content = etree.parse(BytesIO(content), parser=parser)
for link in content.findall("//a"):
    print(f"{link.get('href')} -> {link.text}")
