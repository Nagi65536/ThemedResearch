# 交差点で制御するプログラム

import datetime
import json
from tabnanny import check
import time
from typing import Any
import pytz
import socket
import sqlite3
from concurrent.futures import ThreadPoolExecutor

IPADDR: str = "127.0.0.1"
PORT: int = 65530

sock_sv: socket.socket = socket.socket(socket.AF_INET)
sock_sv.bind((IPADDR, PORT))
sock_sv.listen()

conn = sqlite3.connect('./db/crossroads.db', isolation_level=None)
cur = conn.cursor()

cur.execute(f'''CREATE TABLE IF NOT EXISTS crMain(
    time        INTEGER,
    carId       INTEGER PRIMARY KEY AUTOINCREMENT,
    from_        TEXT,
    to_          TEXT,
    condition   TEXT,
    completion  TEXT
)''')

cur.execute(f'''CREATE TABLE IF NOT EXISTS crTag(
    trafficId TEXT,
    from_N TEXT, from_E TEXT, from_S TEXT, from_W TEXT,
    stop_N TEXT, stop_E TEXT, stop_S TEXT, stop_W TEXT,
    to_N   TEXT, to_E   TEXT, to_S   TEXT, to_W   TEXT
)''')


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


print('⚡ control.py start')
while True:
    # クライアントの接続受付
    sock_cl, addr = sock_sv.accept()

    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(recv_client, sock_cl, addr)