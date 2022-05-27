#!/usr/bin/env python
# encoding: utf-8
"""
@file: file_monitor.py
@time: 2022/5/27 9:57
@project: black-hat-python-2ed
@desc: P191 文件监控
"""
# Modified example, original given here:
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html

import os
import tempfile
import threading
import win32con
import win32file

FILE_CREATED = 1
FILE_DELETED = 2
FILE_MODIFIED = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO = 5

FILE_LIST_DIRECTORY = 0x0001
# 设定要监控的文件夹
PATHS = ['c:\\Windows\\Temp', tempfile.gettempdir()]


def monitor(path_to_watch):
    # 获取指向被监控目录的句柄
    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    while True:
        try:
            # 在目录变动时，提供通知
            results = win32file.ReadDirectoryChangesW(
                h_directory,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY |
                win32con.FILE_NOTIFY_CHANGE_SIZE,
                None,
                None
            )
            # 监控所有文件，并输出被修改的文件名或改动的具体类型
            for action, file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)
                if action == FILE_CREATED:
                    print(f'[+] Created {full_filename}')

                elif action == FILE_DELETED:
                    print(f'[-] Deleted {full_filename}')

                elif action == FILE_MODIFIED:
                    print(f'[*] Modified {full_filename}')
                    try:
                        # 读取文件内容
                        with open(full_filename) as f:
                            contents = f.read()
                        print('[vvv] Dumping contents ... ')
                        print(contents)
                        print('[^^^] Dump complete.')
                    except Exception as e:
                        print(f'[!!!] Dump failed. {e}')

                elif action == FILE_RENAMED_FROM:
                    print(f'[>] Renamed from {full_filename}')
                elif action == FILE_RENAMED_TO:
                    print(f'[<] Renamed to {full_filename}')
                else:
                    print(f'[?] Unknown action on {full_filename}')
        except KeyboardInterrupt:
            break

        except Exception:
            pass


if __name__ == '__main__':
    for path in PATHS:
        monitor_thread = threading.Thread(target=monitor, args=(path,))
        monitor_thread.start()
