#!/usr/bin/env python
# encoding: utf-8
"""
@file: screenshotter.py
@time: 2022/5/26 15:16
@project: black-hat-python-2ed
@desc: P155 截取屏幕
在Windows下运行时，需要将venv/Lib/site-packages/pywin32_system32目录下的pythoncom38.dll、pywintypes38.dll复制到C:\Windows\System32里面
"""

import win32api
import win32con
import win32gui
import win32ui


def get_dimensions():
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return (width, height, left, top)


def screenshot(name='screenshot'):
    # 获取整个桌面的句柄
    hdesktop = win32gui.GetDesktopWindow()
    width, height, left, top = get_dimensions()

    # 创建一个设备上下文
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    # 创建一个基于内存的设备上下文
    mem_dc = img_dc.CreateCompatibleDC()
    # 创建一个位图对象
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)
    # 将桌面图片逐位复制并保存到内存设备上下文中
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
    # 把内存中的图片数据保存到磁盘中
    screenshot.SaveBitmapFile(mem_dc, f'{name}.bmp')

    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())


def run():
    screenshot()
    with open('screenshot.bmp') as f:
        img = f.read()
    return img


if __name__ == '__main__':
    screenshot()
