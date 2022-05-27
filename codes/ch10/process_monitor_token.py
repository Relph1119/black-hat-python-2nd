#!/usr/bin/env python
# encoding: utf-8
"""
@file: process_monitor_token.py
@time: 2022/5/27 9:40
@project: black-hat-python-2ed
@desc: P189 Windows系统的令牌权限
需要Administrators权限执行该程序
"""
import win32con
import wmi
import win32api
import win32security


def get_process_privileges(pid):
    try:
        # 使用进程ID获得指向目标进程的句柄
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
        #打开进程令牌
        htok = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY)
        # 查询该进程的令牌信息
        privs = win32security.GetTokenInformation(htok, win32security.TokenPrivileges)
        privileges = ''
        for priv_id, flags in privs:
            # 判断是否启用标志位
            if flags == win32security.SE_PRIVILEGE_ENABLED | win32security.SE_PRIVILEGE_ENABLED_BY_DEFAULT:
                # 查找这个权限ID对应的权限名称
                privileges += f'{win32security.LookupPrivilegeName(None, priv_id)}|'
    except Exception:
        privileges = 'N/A'

    return privileges


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

            privileges = get_process_privileges(pid)
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
