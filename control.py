# 交差点で制御するプログラム

import json
import select
import socket
import sqlite3
import sys
import time
from typing import Any
from concurrent.futures import ThreadPoolExecutor
import random


DB_NAME = 'main.db'


def indicate_cross_status() -> None:
    conn = sqlite3.connect(F'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()

    map = generate_status_map()

    if len(sys.argv) == 1:
        for i, map_line in enumerate(map):
            for m in map_line:
                if m == '━':
                    print(f'{m}{m}{m}', end='')
                elif m == '─':
                    print(f'{m}{m} ', end='')
                elif m == '┗' or m == '┏':
                    print(f'{m}━━━━', end='')
                elif type(m) == int:
                    print(f' {m:2}', end='')
                else:
                    print(f'{m:2} ', end='')

            print()
        print()


def generate_status_map():
    conn = sqlite3.connect(F'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()

    map = []
    for ml in map_template:
        map.append([m for m in ml])

    cur.execute('SELECT * FROM control')
    res = cur.fetchall()

    in_list = [[0, 0], [0, 0], [0, 0], [0, 0]]
    out_list = [0, 0, 0, 0]
    for data in res:
        if data[5] == 'entry':
            in_list[data[3]][0] += 1
        else:
            in_list[data[3]][1] += 1
        out_list[data[4]] += 1

    # 上 IN
    map[1][10] = in_list[0][0]
    map[3][10] = in_list[0][1]
    # 上 OUT
    map[2][6] = out_list[0]

    # 右 IN
    map[11][15] = in_list[1][0]
    map[11][17] = in_list[1][1]
    # 右 OUT
    map[7][16] = out_list[1]

    # 上 IN
    map[15][6] = in_list[2][0]
    map[17][6] = in_list[2][1]
    # 上 OUT
    map[16][10] = out_list[2]

    # 左 IN
    map[7][1] = in_list[3][0]
    map[7][3] = in_list[3][1]
    # 左 OUT
    map[11][2] = out_list[3]

    return map


def map_draw_line(x, y, dir, map):
    for i in range(10):
        map[y][x] = '*'

        if dir == 0:
            y -= 1
        elif dir == 1:
            x += 1
        elif dir == 2:
            y += 1
        elif dir == 3:
            x -= 1
        elif dir == 4:
            x += 1
            y -= 1
        elif dir == 5:
            x += 1
            y += 1
        elif dir == 6:
            x -= 1
            y += 1
        elif dir == 7:
            x -= 1
            y -= 1

        if i > 1 and dir > 4:
            break
        if x < 0 or x >= len(map[0]):
            break
        elif y < 0 or y >= len(map):
            break


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
    conn = sqlite3.connect(F'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(f'DELETE FROM control WHERE car_id="{car_id}"')


def add_db_control(data: dict) -> None:
    conn = sqlite3.connect(F'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()

    car_id: str = data['car_id']
    tag_id: str = data['tag_id']
    destination: int = data['destination']
    status: str = data['status']
    time_: float = time.time()
    cur.execute(
        f'SELECT cross_name, direction FROM cross_tag_info WHERE tag_id="{tag_id}"')
    get_db_data: dict = cur.fetchone()
    cross_name: str = get_db_data[0]
    origin: int = get_db_data[1]

    cur.execute(f'''
    REPLACE INTO control VALUES (
        "{car_id}", "{cross_name}", "{tag_id}", {origin}, {destination}, "{status}", {time_}
    )''')


def communication(sock: socket.socket, addr: tuple) -> None:
    print(f'【接続】')
    try:
        # 接続報告-受信
        get_data: dict = get_decode_data(sock.recv(1024))
        print(f'{get_data["car_id"]} < {get_data["status"]}')

        # 制御関数の代用
        add_db_control(get_data)

        # TODO 待機なしで進入できる場合の処理

        # 停止指示-送信
        send_data: bytes = get_encode_to_send('stop')
        sock.send(send_data)
        print(f'{get_data["car_id"]} > stop')

        # 進行可能まで待機
        while not (get_data['car_id'] in can_entry_list):
            time.sleep(0.5)

        can_entry_list.remove(get_data['car_id'])
        time.sleep(1)
        # 進入指示-送信
        send_data: bytes = get_encode_to_send('entry')
        sock.send(send_data)
        print(f'{get_data["car_id"]} > entry')

        # 通過済報告-受信
        get_data: dict = get_decode_data(sock.recv(1024))
        print(f'{get_data["car_id"]} < {get_data["status"]}')

    except:
        print(f'{get_data["car_id"]} -communication エラー')

    print(f'【切断】{get_data["car_id"]}')
    remove_db_control(get_data['car_id'])
    # クライアントをクローズ処理
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


def check_can_entry(cross_name) -> None:
    conn = sqlite3.connect(F'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM control WHERE cross_name = "{cross_name}" ORDER BY time ASC')
    control_data = cur.fetchall()

    entry_list = [c for c in control_data if c[5] == 'entry']
    check_list = [c for c in control_data if c[5] != 'entry']

    for my_data in check_list:
        # print(f'car_id: {my_data[0]}')
        can_entry = True

        for you_data in entry_list:
            # 自分と相手が同じ方角からくる場合
            if my_data[3] == you_data[3]:
                can_entry = True
                # print('来る方同じ - 大元許可!')

            elif (my_data[3] + my_data[4]) % 4 == (you_data[3] + you_data[4]) % 4:
                # print('行き先同じ - 大元ブロック!')
                can_entry = False

            # 自分が左折の場合
            elif my_data[4] == 1:
                # print('左折希望')
                can_entry = True

            # 自分が直進の場合
            elif my_data[4] == 2:
                # print('直進希望')
                can_entry = True
                my_left = (my_data[3] + 1) % 4
                you_dest_dir = (you_data[3] + you_data[4]) % 4

                if (you_data[3] == my_left) or (you_dest_dir == my_left):
                    can_entry = False

            elif my_data[4] == 3:
                # print('右折希望')
                can_entry = False

                judge_1 = you_data[3] == (my_data[3] + 1) % 4   # 相手が左から来るか
                judge_2 = you_data[4] == (my_data[3] + 2) % 4   # 相手が前に行くか
                if judge_1 and judge_2:
                    can_entry = True

                judge_1 = you_data[3] == (my_data[3] + 2) % 4   # 相手が前から来るか
                judge_2 = (you_data[3] + you_data[4]
                           ) % 4 == (my_data[3] + 1) % 4   # 相手が左に行くか
                if judge_1 and judge_2:
                    can_entry = True

                judge_1 = you_data[3] == (my_data[3] + 3) % 4   # 相手が右から来るか
                judge_2 = (you_data[3] + you_data[4]
                           ) % 4 == my_data[3]   # 相手が自分側に行くか
                if judge_1 and judge_2:
                    can_entry = True

            else:
                print('未実装だわぼけ！')

            if not can_entry:
                break

        if can_entry:
            # print('--進入可能--')
            # print('')
            entry_list.append(my_data)
            can_entry_list.append(my_data[0])
            cur.execute(
                f'UPDATE control SET status="entry" WHERE car_id="{my_data[0]}"')
        # else:
        #     print('--進入不可--')
        #     print('')
        can_entry = False


def control() -> None:
    conn = sqlite3.connect(F'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('DELETE FROM control')

    while True:
        cur.execute('SELECT cross_name FROM control')
        crosses = [c[0] for c in cur.fetchall()]
        crosses = set(crosses)

        for cross in crosses:
            check_can_entry(cross)

        indicate_cross_status()
        time.sleep(1)


def main() -> None:
    executor = ThreadPoolExecutor()
    executor.submit(control)

    while True:
        # クライアントの接続受付
        sock_cl, addr = sock_sv.accept()
        executor.submit(communication, sock_cl, addr)


if __name__ == '__main__':
    IPADDR: str = "127.0.0.1"
    PORT: int = random.randint(60000, 65535)
    indicate_data = []

    with open('./memo/port_share.txt', 'w') as f:
        f.write(str(PORT))
    print(f'PORT: {PORT}')

    sock_sv: socket.socket = socket.socket(socket.AF_INET)
    sock_sv.bind((IPADDR, PORT))
    sock_sv.listen()

    can_entry_list: list = []
    map_template = [
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", "│",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", " ",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", "│",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", " ",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", "│",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "],
        ["━", "━", "━", "━", "━", "┛", " ", " ", " ", " ",
            " ", " ", " ", "┗", "━", "━", "━", "━", "━"],
        [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
            " ", " ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
            " ", " ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
            " ", " ", " ", " ", " ", " ", " ", " ", " "],
        ["─", " ", "─", " ", "─", " ", " ", " ", " ", "+",
            " ", " ", " ", " ", "─", " ", "─", " ", "─"],
        [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
            " ", " ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
            " ", " ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
            " ", " ", " ", " ", " ", " ", " ", " ", " "],
        ["━", "━", "━", "━", "━", "┓", " ", " ", " ", " ",
            " ", " ", " ", "┏", "━", "━", "━", "━", "━"],
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", "│",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", " ",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", "│",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", " ",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", "┃", " ", " ", " ", "│",
            " ", " ", " ", "┃", " ", " ", " ", " ", " "]
    ]

    print('⚡ control.py start')
    main()
