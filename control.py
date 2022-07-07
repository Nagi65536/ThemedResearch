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


def main():
    while True:
        # クライアントの接続受付
        sock_cl, addr = sock_sv.accept()

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(recv_client, sock_cl, addr)


# データ受信関数
def recv_client(sock: socket.socket, addr: tuple[Any]) -> None:
    print(f'-connected {addr}')

    data_encode: bytes = sock.recv(1024)
    data_decode: str = data_encode.decode('utf-8')
    data = json.loads(data_decode)
    # now: str = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%H:%M.%f')
    print(data)
    wtd = 'stop'
    while wtd == 'stop':
        wtd = input('what to do?\n> ')
        if wtd == 'stop':
            sock.send('stop'.encode('utf-8'))
        else:
            sock.send('ok'.encode('utf-8'))

    data_encode: bytes = sock.recv(1024)
    data_decode: str = data_encode.decode('utf-8')
    data = json.loads(data_decode)
    print(data)

    # クライアントをクローズ処理
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


if __name__ == '__main__':
    sock_sv: socket.socket = socket.socket(socket.AF_INET)
    sock_sv.bind((IPADDR, PORT))
    sock_sv.listen()

    conn = sqlite3.connect('./db/main.db', isolation_level=None)
    cur = conn.cursor()

    print('⚡ control.py start')
    main()
