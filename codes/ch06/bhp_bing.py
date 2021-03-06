#!/usr/bin/env python
# encoding: utf-8
"""
@file: bhp_bing.py
@time: 2022/5/25 10:49
@project: black-hat-python-2ed
@desc: P125 在Burp中调用Bing搜索
"""
from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

import socket
import urllib
import json
import re
import base64

bing_api_key = "你的密钥"


class BurpExtender(IBurpExtender, IContextMenuFactory):
    """
    允许在鼠标右键单击Burp中的请求时提供上下文菜单。
    """

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None

        # 建立扩展工具
        callbacks.setExtensionName("Use Bing")
        callbacks.registerContextMenuFactory(self)
        return

    # 创建菜单并处理点击事件，就是actionPerformed那里，点击调用bing_menu函数
    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        # 下个步骤是简历createMenuItem函数，
        # 该函数接受IContextMenuInvocation对象，用来判定用户选中了哪个HTTP请求。最后一个步骤用来
        # 渲染的菜单，并让的bing_menu函数处理点击事件。
        return menu_list

    def bing_menu(self, event):
        # 获取用户点击的详细信息
        # 当用户点击定义的上下文菜单时，bing_menu函数将被激活。接受所有高亮显示的HTTP请求
        # 然后检索每一个请求的域名部分并将它们发送到bing_search函数进行进一步处理。

        http_traffic = self.context.getSelectedMessages()

        print("%d requests highlighted" % len(http_traffic))

        # 获取ip或主机名(域名)
        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()

            print("User selected host: %s" % host)

            self.bing_search(host)

        return

    def bing_search(self, host):
        # 检查参数是否为ip地址或主机名（域名）
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)
        # bing_search函数首先判定传输的是否是IP地址或是域名
        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True

        # 查寻同一ip是否存在不同虚拟机
        bing_query_string = "'ip:%s'" % ip_address
        self.bing_query(bing_query_string)

        # 若为域名则执行二次搜索，搜索子域名
        if domain:
            bing_query_string = "'domain:%s'" % host
            self.bing_query(bing_query_string)

    def bing_query(self, bing_query_string):
        print("Performing Bing search: %s" % bing_query_string)
        # 编码的查询(如　urllib.quote('ab c')－－＞　'ab%20c')
        quoted_query = urllib.quote(bing_query_string)

        http_request = "GET https://api.datamarket.azure.com/Bing/Search/Web?$format=json&$top=20&Query=%s HTTP/1.1\r\n" % quoted_query
        http_request += "Host: api.datamarket.azure.com\r\n"
        http_request += "Connection: close\r\n"
        # 对API密钥使用base64编码
        http_request += "Authorization: Basic %s\r\n" % base64.b64encode(":%s" % bing_api_key)
        http_request += "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36\r\n\r\n"

        json_body = self._callbacks.makeHttpRequest("api.datamarket.azure.com", 443, True, http_request).tostring()

        # 去掉HTTP响应头，只取正文
        json_body = json_body.split("\r\n\r\n", 1)[1]

        # print json_body

        try:
            # 传递给json解析器
            r = json.loads(json_body)

            # 输出查询到的网站的相关信息
            if len(r["d"]["results"]):
                for site in r["d"]["results"]:
                    print("*" * 100)
                    print(site['Title'])
                    print(site['Url'])
                    print(site['Description'])
                    print("*" * 100)

                    j_url = URL(site['Url'])

            # 如果网站不在brup的目标列表中，就添加进去
            # 将Jython API和纯Python 组合添加到Burp扩展工具中，在攻击特定目标的时候
            # 用来做进一步的侦查非常使用.
            if not self._callbacks.isInScope(j_url):
                print("Adding to Burp scope")
                self._callbacks.includeInScope(j_url)
        except:
            print("No results from Bing")
            pass

        return
