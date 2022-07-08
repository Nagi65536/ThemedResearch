# 交差点で制御するプログラム

import datetime
import json
import time
from typing import Any
import pytz
import socket
import sqlite3
from concurrent.futures import ThreadPoolExecutor

IPADDR: str = "127.0.0.1"
PORT: int = 65530


def communication(sock: socket.socket, addr: tuple[Any]) -> None:
    print(f'【connected】{addr}')

    # 接続報告-受信
    get_data = get_decode_data(sock.recv(1024))
    print(get_data)

    # 停止指示-送信
    send_data = get_encode_to_send('stop')
    sock.send(send_data)

    time.sleep(2)
    can_entry_list.append(get_data['carid'])
    print(can_entry_list)

    # 進行可能まで待機
    while not (get_data['carid'] in can_entry_list):
        time.sleep(0.5)

    # 進入指示-送信
    send_data = get_encode_to_send('entry')
    sock.send(send_data)

    # 通過済報告-受信
    get_data = get_decode_data(sock.recv(1024))
    print(get_data)

    # クライアントをクローズ処理
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


def get_encode_to_send(operate):
    data = {'operate': operate}
    data_json: str = json.dumps(data)
    data_encode: bytes = data_json.encode('utf-8')

    return data_encode


def get_decode_data(data):
    data_decode: str = data.decode('utf-8')
    data_py_obj = json.loads(data_decode)

    return data_py_obj


def control(data: json):
    print(data)


def main():
    while True:
        # クライアントの接続受付
        sock_cl, addr = sock_sv.accept()

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(communication, sock_cl, addr)


if __name__ == '__main__':
    sock_sv: socket.socket = socket.socket(socket.AF_INET)
    sock_sv.bind((IPADDR, PORT))
    sock_sv.listen()

    conn = sqlite3.connect('./db/main.db', isolation_level=None)
    cur = conn.cursor()

    can_entry_list = []

    print('⚡ control.py start')
    main()
