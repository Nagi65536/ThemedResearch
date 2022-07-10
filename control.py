# 交差点で制御するプログラム

import json
import select
import socket
import sqlite3
import time
from typing import Any
from concurrent.futures import ThreadPoolExecutor

IPADDR: str = "127.0.0.1"
PORT: int = 65530

sock_sv: socket.socket = socket.socket(socket.AF_INET)
sock_sv.bind((IPADDR, PORT))
sock_sv.listen()

can_entry_list: list = []


def get_encode_to_send(operate) -> bytes:
    data: dict = {'operate': operate}
    data_json: str = json.dumps(data)
    data_encode: bytes = data_json.encode('utf-8')

    return data_encode


def get_decode_data(data) -> dict:
    data_decode: str = data.decode('utf-8')
    data_py_obj: dict = json.loads(data_decode)

    return data_py_obj


def remove_db_control(car_id: str) -> None:
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    cur = conn.cursor()

    cur.execute(f'DELETE FROM control WHERE car_id="{car_id}"')


def add_db_control(data: dict) -> str:
    conn = sqlite3.connect('./db/main.db', isolation_level=None)
    cur = conn.cursor()

    car_id: str = data['car_id']
    tag_id: str = data['tag_id']
    destination: int = data['destination']
    time_: float = time.time()

    cur.execute(f'SELECT cross_name, direction FROM tag_info WHERE tag_id = "{tag_id}"')
    get_db_data: dict = cur.fetchone()
    cross_name: str = get_db_data[0]
    origin: int = get_db_data[1]
    dest_direction: int = origin + destination

    cur.execute(f'''
    REPLACE INTO control VALUES (
        "{car_id}", "{cross_name}", "{tag_id}", "{origin}", "{destination}", "{status}", {time_}
    )''')

    return cross_name


def communication(sock: socket.socket, addr: tuple) -> None:
    print(f'【connected】{addr}')

    try:
        # 接続報告-受信
        get_data: dict = get_decode_data(sock.recv(1024))
        print(get_data)

        # 制御関数の代用
        cross_name: str = add_db_control(get_data)
        time.sleep(2)
        can_entry_list.append(get_data['car_id'])
        print(can_entry_list)

        # 待機なしで進入できるか
        # can_entry(get_data, cross_name)

        # 停止指示-送信
        send_data: bytes = get_encode_to_send('stop')
        sock.send(send_data)
        # 仮の時間稼ぎ
        time.sleep(2)

        # 進行可能まで待機
        while not (get_data['car_id'] in can_entry_list):
            time.sleep(0.5)

        # 進入指示-送信
        send_data: bytes = get_encode_to_send('entry')
        sock.send(send_data)

        # 通過済報告-受信
        get_data: dict = get_decode_data(sock.recv(1024))
        print(get_data)

    except ConnectionResetError as e:
        print(e)

    print(f'【切断】{addr}')
    # クライアントをクローズ処理
    remove_db_control(get_data['car_id'])
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


def control() -> None:
    conn = sqlite3.connect('./db/main.db', isolation_level=None)
    cur = conn.cursor()
    # cur.execute('DELETE FROM control')
    print('-control')

    while True:
        cur.execute('SELECT cross_name FROM control')
        crosses = [c[0] for c in cur.fetchall()]
        crosses = set(crosses)
        # print(crosses)

        for cross in crosses:
            cur.execute(f'SELECT * FROM control WHERE cross_name = "{cross}"')
            control_data = cur.fetchall()
            control_data = sorted(control_data, reverse=False, key=lambda x: x[5])
            entry_list = [c for c in control_data if c[4]=='entry']

            # TODO
            for c in control_data:
                # print(c)
                pass
            
        time.sleep(2)


def main() -> None:
    executor = ThreadPoolExecutor()
    executor.submit(control)
    while True:
        # クライアントの接続受付
        sock_cl, addr = sock_sv.accept()
        executor.submit(communication, sock_cl, addr)


if __name__ == '__main__':
    print('⚡ control.py start')
    main()
