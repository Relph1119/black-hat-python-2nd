#!/usr/bin/env python
# encoding: utf-8
"""
@file: sandbox_detect.py
@time: 2022/5/26 16:57
@project: black-hat-python-2ed
@desc: P160 沙箱检测
目的：判断沙箱的操作者是否再重复某些相同的输入以绕过一些初级的沙箱检测方案，判断木马是不是在一个沙箱中，决定木马是否还要继续执行
"""
import random
import sys
import time
from ctypes import Structure, c_uint, c_ulong, sizeof, windll, byref
import win32api


class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_ulong)
    ]


def get_last_input():
    struct_lastinputinfo = LASTINPUTINFO()
    # 初始化结构体的大小
    struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO)
    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))
    # 计算系统运行的时间
    run_time = windll.kernel32.GetTickCount()
    elapsed = run_time - struct_lastinputinfo.dwTime
    print(f"[*] It's been {elapsed} milliseconds since the last event.")
    return elapsed


class Detector:
    def __init__(self):
        self.double_clicks = 0
        self.keystorkes = 0
        self.mouse_clicks = 0

    def get_key_press(self):
        # 遍历所有可用的键
        for i in range(0, 0xff):
            # 获取该键的状态
            state = win32api.GetAsyncKeyState(i)
            # 判断该键是否按下
            if state & 0x0001:
                if i == 0x1:
                    # 判断鼠标左键被单击
                    self.mouse_clicks += 1
                    return time.time()
                elif 32 < i < 127:
                    # 该键是否是键盘上的ASCII按键
                    self.keystorkes += 1
        return None

    def detect(self):
        previous_timestampe = None
        first_double_click = None
        double_click_threshold = 0.35

        # 鼠标双击的沙箱检测阈值
        max_double_clicks = 10
        # 敲击键盘的沙箱检测阈值
        max_keystrokes = random.randint(10, 25)
        # 单击鼠标的沙箱检测阈值
        max_mouse_clicks = random.randint(5, 25)
        max_input_threshold = 30000

        # 获取上一次用户输入以来经过的时间
        last_input = get_last_input()
        # 时间过长，就自动退出，结束木马执行
        if last_input >= max_input_threshold:
            sys.exit(0)

        detection_complete = False
        while not detection_complete:
            keypress_time = self.get_key_press()
            # 判断是否发生按键或鼠标单击事件
            if keypress_time is not None and previous_timestampe is not None:
                # 计算两次事件之间的事件
                elapsed = keypress_time - previous_timestampe

                # 检测鼠标双击事件
                if elapsed <= double_click_threshold:
                    self.mouse_clicks -= 2
                    self.double_clicks += 1
                    if first_double_click is None:
                        first_double_click = time.time()
                    else:
                        # 是否发生一连串的鼠标单击事件
                        if self.double_clicks >= max_double_clicks:
                            # 如果短时间内鼠标双击事件达到了最大值，就强制退出
                            if keypress_time - first_double_click <= (max_double_clicks * double_click_threshold):
                                sys.exit(0)
                # 检测按键次数、鼠标单击和双击数是否都达到了最大值，强制退出
                if (self.keystorkes >= max_keystrokes and
                        self.double_clicks >= max_double_clicks and
                        self.mouse_clicks >= max_mouse_clicks):
                    detection_complete = True

                previous_timestampe = keypress_time
            elif keypress_time is not None:
                previous_timestampe = keypress_time


if __name__ == '__main__':
    d = Detector()
    d.detect()
    print("okay.")
