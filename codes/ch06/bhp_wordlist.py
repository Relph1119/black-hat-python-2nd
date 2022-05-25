#!/usr/bin/env python
# encoding: utf-8
"""
@file: bhp_wordlist.py
@time: 2022/5/25 10:53
@project: black-hat-python-2ed
@desc: P132 利用网页内容生成暴破字典
"""

from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList

import re
from datetime import datetime
from HTMLParser import HTMLParser


#   TagStripper 类允许去掉HTTP响应包中的HTML标签
class TagStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.page_text = []

    def handle_data(self, data):
        """
        遇到两个标签之间的数据时调用，将页面的文本内容存储到变量中
        :param data:
        :return:
        """
        self.page_text.append(data)

    def handle_comment(self, data):
        """
        遇到注释时调用，将开发者注释的内容添加到字典中，调用了handle_data 函数（以便在处理的过程中想改变处理页面的方式）
        :param data:
        :return:
        """
        self.handle_data(data)

    def strip(self, html):
        """
        将HTML代码填充到HTMLParser基类中，返回结果页面的文本内容
        :param html:
        :return:
        """
        self.feed(html)
        return "".join(self.page_text)


class BurpExtender(IBurpExtender, IContextMenuFactory):
    """
    在Burp的图像页面中添加右键菜单，
    """
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None
        self.hosts = set()
        # 初始化字典的集合并将它设置成最常用的密码：password，保证它是字典中的最后一个词
        # 先设定一个非常常见的密码，因为是字典，不能重复最好，所以用集合
        self.wordlist = set(["password"])

        # 建立起的扩展工具
        callbacks.setExtensionName("Build Wordlist")
        callbacks.registerContextMenuFactory(self)

        return

    # 添加菜单
    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Bulid Wordlist", actionPerformed=self.wordlist_menu))

        return menu_list

    #   现在添加逻辑控制，将选择的HTTP流量通过Burp转换成一个基本的字典.
    #   wordlist_menu函数处理点击菜单事件.
    def wordlist_menu(self, event):

        # 抓取用户点击细节
        http_traffic = self.context.getSelectedMessages()

        #   获取ip或主机名(域名)
        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()
            #   它存储目标响应主机的名字.
            self.hosts.add(host)
            #   获取网站的返回信息
            http_response = traffic.getResponse()
            #   若有回应就调用get_word
            if http_response:
                #   然后检索HTTP响应的内容并发送给get_words函数.
                self.get_words(http_response)

        self.display_wordlist()
        return

    def get_words(self, http_response):

        headers, body = http_response.tostring().split("\r\n\r\n", 1)

        #   忽略下一个请求
        #   get_words函数去掉响应信息的HTTP头部，确保仅对响应的文本内容进行处理
        if headers.lower().find("content-type: text") == -1:
            return

        #   获取标签中的文本
        tag_stripper = TagStripper()
        #   TagStripper类将HTTP代码从剩下的页面文本中去除.
        page_text = tag_stripper.strip(body)
        #   使用正则表达式查找所有以字母开头后面跟着两个或者多个“单词”的字符
        #   匹配第一个是字母的，后面跟着的是两个以上的字母，数字或下划线／
        words = re.findall("[a-zA-Z]\w{2,}", page_text)

        for word in words:
            # 过滤长字符串
            if len(word) <= 15:
                #   完成最后的整理后，字符将以小写形式存储到字典(wordlist)中.
                self.wordlist.add(word.lower())

        return

    #   再后面添加更多的猜测
    #   mangle函数基于一些基本的密码生成“策略”将一个基础的单词转换成一类猜测密码。
    def mangle(self, word):
        #   在这个简单的例子中，创建了在基础单词上添加后缀的列表，包括当前的年份.
        year = datetime.now().year
        suffixes = ["", "1", "!", year]
        mangled = []
        #   做循环，将每个后缀添加到基础单词的后面.这样就创建了可尝试的新密码
        for password in (word, word.capitalize()):
            for suffix in suffixes:
                mangled.append("%s%s" % (password, suffix))

        return mangled

    def display_wordlist(self):
        #   输出用于生成密码字典的网站的名字
        #   处理每一个基础单词并输出结果
        print("#!comment: BHP Wordlist for site(s) %s" % ", ".join(self.hosts))

        for word in sorted(self.wordlist):
            for password in self.mangle(word):
                print(password)

        return
