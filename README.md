# 《Python黑帽子-黑客与渗透测试编程之道》笔记

&emsp;&emsp;《Python黑帽子-黑客与渗透测试编程之道》先介绍了网络方面的基础知识和原始socket、著名的网络工具scapy；通过讲解python的网络库（urllib、requests、lxml和BeautifulSoup）的使用，扫描网络系统结构、破解目录和文件位置、破解HTML登录表单等场景；介绍Burp Suite并编写攻击插件，并基于GitHub服务的C&C通信的木马编写，讨论在Windows下的木马常用功能，以及Windows的系统提权；还介绍了数据渗漏和攻击取证相关的渗透。

## 运行环境
### Python版本
Mini-Conda Python 3.8 Windows环境

### 批量导入环境依赖包
```shell
pip install -r requirements.txt
```

### 批量导出环境中所有依赖包
```shell
pip freeze > requirements.txt
```