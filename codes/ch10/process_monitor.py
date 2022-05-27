#!/usr/bin/env python
# encoding: utf-8
"""
@file: process_monitor.py
@time: 2022/5/27 9:40
@project: black-hat-python-2ed
@desc: P185 利用WMI监视进程
需要Administrators权限执行该程序
"""

import wmi


def log_to_file(message):
    with open('process_monitor_log.csv', 'a') as fd:
        fd.write(f'{message}\r\n')


def monitor():
    log_to_file('CommandLine, Time, Executable, Parent PID, PID, User, Privileges')
    # 创建WMI实例
    c = wmi.WMI()
    # 监控进程创建事件
    process_watcher = c.Win32_Process.watch_for('creation')
    while True:
        try:
            # 循环等待返回一个新的进程事件
            new_process = process_watcher()
            # 获取进程的全部信息
            cmdline = new_process.CommandLine
            create_date = new_process.CreationDate
            executable = new_process.ExecutablePath
            parent_pid = new_process.ParentProcessId
            pid = new_process.ProcessId
            proc_owner = new_process.GetOwner()

            privileges = 'N/A'
            process_log_message = (
                f'{cmdline} , {create_date} , {executable},'
                f'{parent_pid} , {pid} , {proc_owner} , {privileges}'
            )
            print(process_log_message)
            print()
            # 记录到日志文件中
            log_to_file(process_log_message)
        except Exception:
            pass


if __name__ == '__main__':
    monitor()
