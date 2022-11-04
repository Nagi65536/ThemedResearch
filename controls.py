# 交差点で制御するプログラム

import json
import math
import socket
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import random


DB_NAME = 'sub.db'
PROCESS_DELAY = 0.1
TRAFFIC_LIGHT_TIME = [10, 10, 10, 10]


def add_log(log):
    with open(f'log/{LOG_FILE}', 'a') as f:
        f.writelines(log + '\n')


def get_encode_data(car_id, operate) -> bytes:
    data: dict = {'car_id': car_id, 'operate': operate}
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
    dest_list = ['n', 'e', 's', 'w']
    add_log(
        f'{car_id} connect {time.time() - start_time:3.2f} [{dest_list[origin]} -> {destination}]')


def client_passed(get_data):
    remove_db_control(get_data['car_id'])
    print(f'{get_data["car_id"]} > passed')
    print(f'【切断】 {get_data["car_id"]}')

    add_log(f'{get_data["car_id"]} passed  {time.time() - start_time:3.2f}')


def client_entry(data):
    conn = sqlite3.connect(f'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()

    send_data: bytes = get_encode_data(data[0], 'entry')
    sock.send(send_data)
    cur.execute(
        f'UPDATE control SET status="entry" WHERE car_id="{data[0]}"')
    print(f'{data[0]} < entry')
    entry_times.append({'car_id': data[0], 'time': time.time()})

    add_log(f'{data[0]} entry   {time.time() - start_time:3.2f}')


def client_connect(get_data):
    print(f'【接続】 {get_data["car_id"]}')
    print(f'{get_data["car_id"]} > connect')
    add_db_control(get_data)

    send_data: bytes = get_encode_data(get_data["car_id"], 'stop')
    sock.send(send_data)
    print(f'{get_data["car_id"]} < stop')


def communication(get_data) -> None:
    print('-----【処理開始】----------')

    global start_time
    if not start_time:
        start_time = time.time()

    try:
        if get_data["status"] == 'connect':
            client_connect(get_data)

        elif get_data["status"] == 'passed':
            client_passed(get_data)
    except:
        print('【ERROR】')
    print('-----【処理完了】----------')


def control_traffic_lights(cross_name) -> None:
    conn = sqlite3.connect(f'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM control WHERE cross_name="{cross_name}" AND status!="entry" ORDER BY time ASC')
    control_data = cur.fetchall()

    global can_entry_origin
    can_entry_origin += 1
    tmp_can_entry_origin = math.floor((can_entry_origin / 20) % 2)

    for data in control_data:
        if data[3] == tmp_can_entry_origin or data[3] == tmp_can_entry_origin+2:
            client_entry(data)


def check_can_entry(cross_name) -> None:
    conn = sqlite3.connect(f'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM control WHERE cross_name = "{cross_name}" ORDER BY time ASC')
    control_data = cur.fetchall()

    entry_list = [c for c in control_data if c[5] == 'entry']
    check_list = [c for c in control_data if c[5] != 'entry']

    # tmp_1_check_list = [c for c in check_list if check_list[0][3] == c[3]]
    # tmp_2_check_list = [c for c in check_list if check_list[0][3] != c[3]]

    for my_data in check_list:
        can_entry = True

        for you_data in entry_list:
            if my_data[3] == you_data[3]:
                can_entry = True

            elif (my_data[3] + my_data[4]) % 4 == (you_data[3] + you_data[4]) % 4:
                can_entry = False

            elif my_data[4] == 1:
                can_entry = True

            elif my_data[4] == 2:
                can_entry = True
                my_left = (my_data[3] + 1) % 4
                you_dest_dir = (you_data[3] + you_data[4]) % 4

                if (you_data[3] == my_left) or (you_dest_dir == my_left):
                    can_entry = False

            elif my_data[4] == 3:
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
            entry_list.append(my_data)
            client_entry(my_data)


def control() -> None:
    conn = sqlite3.connect(F'./db/{DB_NAME}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('DELETE FROM control')

    while True:
        cur.execute('SELECT cross_name FROM control')
        crosses = [c[0] for c in cur.fetchall()]
        crosses = set(crosses)

        for cross in crosses:
            if len(arg) > 1 and arg[1] == 'tl':
                control_traffic_lights(cross)
            else:
                check_can_entry(cross)

        time.sleep(PROCESS_DELAY)


def main() -> None:
    with ThreadPoolExecutor() as executor:
        executor.submit(control)

        while True:
            get_data: dict = get_decode_data(sock.recv(1024))
            executor.submit(communication, get_data)


if __name__ == '__main__':
    IPADDR: str = "127.0.0.1"
    PORT: int = random.randint(60000, 65535)
    indicate_data = []
    LOG_FILE = None
    arg = sys.argv

    if len(arg) > 1 and arg[1] == 'tl':
        LOG_FILE = 'traffic-light.log'
    else:
        LOG_FILE = 'timepri.log'

    with open('./memo/port_share.txt', 'w') as f:
        f.write(str(PORT))
    with open('./memo/logfile_share.txt', 'w') as f:
        f.write(LOG_FILE)

    print('⚡ control.py start')
    sock_sv: socket.socket = socket.socket(socket.AF_INET)
    sock_sv.bind((IPADDR, PORT))
    sock_sv.listen()
    sock, addr = sock_sv.accept()

    control_counter = 0
    can_entry_origin = 0

    start_time = None
    entry_times = []

    main()
