#!/usr/bin/env python
# encoding: utf-8
"""
@file: tcp_server.py
@time: 2022/5/23 10:02
@project: black-hat-python-2ed
@desc: P12，TCP服务端
"""
import socket
import threading

IP = "0.0.0.0"
PORT = 9998


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 指定监听IP地址和端口
    server.bind((IP, PORT))
    # 让服务器开始监听，允许的最大客户端连接数设置为5
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')


if __name__ == '__main__':
    main()
