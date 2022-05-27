#!/usr/bin/env python
# encoding: utf-8
"""
@file: bhservice.py
@time: 2022/5/27 8:45
@project: black-hat-python-2ed
@desc: P182 模拟受害服务
使用命令打包：pyinstaller -F --hiddenimport win32timezone bhservice.py
在Windows系统中，使用超级管理员执行命令安装服务：bhservice.exe install
启动服务：bhservice.exe start
停止服务：bhservice.exe stop
删除服务：bhservice.exe remove
"""
import os.path
import shutil
import subprocess
import sys

import win32event
import win32service
import win32serviceutil
import servicemanager

SRCDIR = "E:\\LearningDisk\\Learning_More"
TGTDIR = "C:\\Windows\\TEMP"


class BHServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "BlackHatService"
    _svc_display_name_ = "Black Hat Service"
    _svc_description_ = ("Executes VBScripts at regular intervals." +
                         " What could possibly go wrong?")

    def __init__(self, args):
        # 设定脚本运行的位置
        self.vbs = os.path.join(TGTDIR, 'bhservice_task.vbs')
        # 设定1分钟的超时时间
        self.timeout = 1000 * 60

        win32serviceutil.ServiceFramework.__init__(self, args)
        # 创建一个事件对象
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        # 设定服务状态
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # 停止该服务
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # 启动服务
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # 调用服务要运行的main函数
        self.main()

    def main(self):
        # 开启一个循环，每分钟运行一次
        while True:
            ret_code = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # 当收到停止信号时，停止服务
            if ret_code == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg("Service is stopping")
                break
            src = os.path.join(SRCDIR, 'bhservice_task.vbs')
            # 将脚本复制到目标目录
            shutil.copy(src, self.vbs)
            os.unlink(self.vbs)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BHServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BHServerSvc)
