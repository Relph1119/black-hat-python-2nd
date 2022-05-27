#!/usr/bin/env python
# encoding: utf-8
"""
@file: cryptor.py
@time: 2022/5/26 18:28
@project: black-hat-python-2ed
@desc: P166 文件内容的加密和解密
"""
import base64
import zlib

from Cryptodome.Cipher import PKCS1_OAEP, AES
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from io import BytesIO


def generate():
    """
    生成RSA密钥
    :return:
    """
    new_key = RSA.generate(2048)
    private_key = new_key.exportKey()
    public_key = new_key.publickey().exportKey()

    with open('./ras_key/key.pri', 'wb') as f:
        f.write(private_key)

    with open('./ras_key/key.pub', 'wb') as f:
        f.write(public_key)


def get_ras_cipher(keytype):
    """
    加载私钥或公钥
    :param keytype:
    :return:
    """
    with open(f'./ras_key/key.{keytype}') as f:
        key = f.read()
    rsakey = RSA.importKey(key)
    return PKCS1_OAEP.new(rsakey), rsakey.size_in_bytes()


def encrypt(plaintext):
    # 将明文数据以bytes类型传入并压缩
    compressed_text = zlib.compress(plaintext)

    # 随机生成会话密钥
    session_key = get_random_bytes(16)
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    # 使用该密码对压缩过的明文加密
    ciphertext, tag = cipher_aes.encrypt_and_digest(compressed_text)

    cipher_rsa, _ = get_ras_cipher('pub')
    # 使用RSA公钥对会话密钥进行加密
    encrypted_session_key = cipher_rsa.encrypt(session_key)
    # 将所有的信息都打包到一个载荷中
    msg_payload = encrypted_session_key + cipher_aes.nonce + tag + ciphertext
    # 对载荷进行base64编码
    encrypted = base64.encodebytes(msg_payload)
    return encrypted


def decrypt(encrypted):
    # 将base64将字符串解码为bytes数据
    encrypted_bytes = BytesIO(base64.decodebytes(encrypted))
    cipher_rsa, keysize_in_bytes = get_ras_cipher('pri')

    # 从数据中读取加密后的会话密钥，解密所需的其他参数
    encrypted_session_key = encrypted_bytes.read(keysize_in_bytes)
    nonce = encrypted_bytes.read(16)
    tag = encrypted_bytes.read(16)
    ciphertext = encrypted_bytes.read()

    # 使用RSA私钥解密会话密钥
    session_key = cipher_rsa.decrypt(encrypted_session_key)
    # 使用密钥执行AES算法，解码数据正文
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    decrypted = cipher_aes.decrypt_and_verify(ciphertext, tag)

    # 解压为消息明文
    plaintext = zlib.decompress(decrypted)
    return plaintext


if __name__ == '__main__':
    # 生成公钥和私钥
    # generate()
    plaintext = b'hey there you.'
    print(decrypt(encrypt(plaintext)))
