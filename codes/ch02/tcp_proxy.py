#!/usr/bin/env python
# encoding: utf-8
"""
@file: tcp_proxy.py
@time: 2022/5/23 14:10
@project: black-hat-python-2ed
@desc: P22 TCP代理
"""

# 在所有可打印字符的位置，保持原有字符不变；在所有不可打印的字符位置，放上一个句点
import socket
import sys
import threading

HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])


def hexdump(src, length=16, show=True):
    """
    接收bytes或string类型的输入，将其转换为十六进制格式输出到屏幕上
    提供实时观察代理内数据流通
    :param src:
    :param length:
    :param show:
    :return:
    """
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i + length])
        # 转换成可打印字符的格式
        printable = word.translate(HEX_FILTER)
        # 转换成十六进制
        hexa = ''.join([f'{ord(c):02X}' for c in word])
        hexwidth = length * 3
        # 将word变量的起始点偏移、其十六进制表示和可打印字符表示形式打包成一行字符串
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results


def receive_from(connection):
    """
    从代理的两端接收数据
    :param connection:
    :return:
    """
    buffer = b''
    # 设置超时时间为5秒
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    """
    请求数据包
    :param buffer:
    :return:
    """
    return buffer


def response_handler(buffer):
    """
    回复数据包
    :param buffer:
    :return:
    """
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接远程主机
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    # （1）开启一个循环
    # （2）不断地从本地客户端读取数据，处理数据，再转发给远程服务器，
    # （3）从远程服务器读取数据，处理数据，再转发给本地客户端
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # 将新连接交给proxy_handler函数，由它来给数据流的两端收发数据
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] ", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit()

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()
