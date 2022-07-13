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
    conn = sqlite3.connect('./db/main.db', isolation_level=None)
    cur = conn.cursor()

    cur.execute(f'DELETE FROM control WHERE car_id="{car_id}"')


def add_db_control(data: dict) -> None:
    conn = sqlite3.connect('./db/main.db', isolation_level=None)
    cur = conn.cursor()

    car_id: str = data['car_id']
    tag_id: str = data['tag_id']
    destination: int = data['destination']
    status: str = data['status']
    time_: float = time.time()
    cur.execute(
        f'SELECT cross_name, direction FROM tag_info WHERE tag_id = "{tag_id}"')
    get_db_data: dict = cur.fetchone()
    cross_name: str = get_db_data[0]
    origin: int = get_db_data[1]

    cur.execute(f'''
    REPLACE INTO control VALUES (
        "{car_id}", "{cross_name}", "{tag_id}", {origin}, {destination}, "{status}", {time_}
    )''')


def communication(sock: socket.socket, addr: tuple) -> None:
    print(f'【connected】{addr}')

    try:
        # 接続報告-受信
        get_data: dict = get_decode_data(sock.recv(1024))
        # print()
        # print('*connect', get_data)

        # 制御関数の代用
        add_db_control(get_data)

        # TODO 待機なしで進入できる場合の処理

        # 停止指示-送信
        send_data: bytes = get_encode_to_send('stop')
        sock.send(send_data)

        # 進行可能まで待機
        while not (get_data['car_id'] in can_entry_list):
            time.sleep(0.5)

        can_entry_list.remove(get_data['car_id'])
        time.sleep(1)
        # 進入指示-送信
        send_data: bytes = get_encode_to_send('entry')
        sock.send(send_data)

        # 通過済報告-受信
        get_data: dict = get_decode_data(sock.recv(1024))
        # print()
        # print('*passed', get_data)
        remove_db_control(get_data['car_id'])

    except:
        print('-communication エラー')

    print()
    print(f'【切断】{addr}')
    # クライアントをクローズ処理
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


def check_can_entry(cross_name) -> None:
    # TODO conn,cur を global でグローバル化す
    conn = sqlite3.connect('./db/main.db', isolation_level=None)
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM control WHERE cross_name = "{cross_name}" ORDER BY time ASC')
    control_data = cur.fetchall()

    entry_list = [c for c in control_data if c[5] == 'entry']
    check_list = [c for c in control_data if c[5] != 'entry']
    control_data = entry_list + check_list

    for my_data in check_list:
        print()
        print('my_car_id:', my_data[0])
        can_entry = True

        for you_data in entry_list:
            # 自分と相手が同じ方角からくる場合
            print('you', you_data[3])
            print('my', my_data[3])
            if my_data[3] == you_data[3]:
                print('来る方同じ - 大元ブロック!')

            elif (my_data[3] + my_data[4]) % 4 == (you_data[3] + you_data[4]) % 4:
                print('行き先同じ - 大元ブロック!')
                can_entry = False

            # 自分が左折の場合
            elif my_data[4] == 1:
                print('左折希望')
                # my_dest_dir = (my_data[3] + my_data[4]) % 4  # 自分の行き先（絶対）
                # you_dest_dir = (you_data[3] + you_data[4]) % 4  # 相手の行き先（絶対）

                # if my_dest_dir == you_dest_dir:
                #     can_entry = False
                #     break

            # 自分が直進の場合
            elif my_data[4] == 2:
                print('直進希望')
                my_left = (my_data[3] + 1) % 4
                you_dest_dir = (you_data[3] + you_data[4]) % 4

                if (you_data[3] == my_left) or (you_dest_dir == my_left):
                    can_entry = False

            elif my_data[4] == 3:
                print('右折希望')
                can_entry = False

                judge_1 = you_data[3] == (my_data[3] + 1) % 4   # 相手が左から来るか
                judge_2 = you_data[4] == (my_data[3] + 2) % 4   # 相手が前に行くか
                if judge_1 and judge_2:
                    print('if 1つ目')
                    can_entry = True

                print('ok1')
                judge_1 = you_data[3] == (my_data[3] + 2) % 4   # 相手が前から来るか
                judge_2 = (you_data[3]+ you_data[4]) % 4 == (my_data[3] + 1) % 4   # 相手が左に行くか
                if judge_1 and judge_2:
                    print('if 2つ目')
                    can_entry = True

                print('ok2')
                judge_1 = you_data[3] == (my_data[3] + 3) % 4   # 相手が右から来るか
                judge_2 = (you_data[3] + you_data[4]) % 4 == my_data[3]   # 相手が自分側に行くか
                if judge_1 and judge_2:
                    print('if 3つ目')
                    can_entry = True

                print('どれもちがうのかい！')

            else:
                print('まだだわぼけ')

        if can_entry:
            print('--進入可能--')
            can_entry_list.append(my_data[0])
            cur.execute(
                f'UPDATE control SET status="entry" WHERE car_id="{my_data[0]}"')
        else:
            print('--進入不可--')
        can_entry = False


def control() -> None:
    conn = sqlite3.connect('./db/main.db', isolation_level=None)
    cur = conn.cursor()
    # cur.execute('DELETE FROM control')
    print('【control】')

    while True:
        cur.execute('SELECT cross_name FROM control')
        crosses = [c[0] for c in cur.fetchall()]
        crosses = set(crosses)

        for cross in crosses:
            check_can_entry(cross)

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
