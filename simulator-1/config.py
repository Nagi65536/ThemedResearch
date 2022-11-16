import sqlite3
import sys
import time
import random


# ログファイルのパス
LOG_FILE_PATH = f'../log/simulator-1'
# データベースのパス
DB_PATH = '../db/simulator1.db'
# 処理の遅延
PROCESS_DELAY = 0.1
# 前方の車1台あたりの遅延
ENTRY_DELAY = 0.5
# 交差点を通過するまでの時間
CAR_PASSED_TIME = 2
# 信号機の時間(南北, 東西)
TRAFFIC_LIGHT_TIME = (4, 4)
# 黄色の時間
TRAFFIC_LIGHT_TIME_YELLOW = 2
# クライアントの時間差をランダムにした時の範囲
DELAY_RANGE = (0, 2)
# クライアントデータ
clients = [
    # 前の車との出発時間の差, スタート位置, ゴール位置
    {'delay': None, 'start': None, 'goal': None},
    {'delay': None, 'start': None, 'goal': None},
    {'delay': None, 'start': None, 'goal': None},
    {'delay': None, 'start': None, 'goal': None},
    {'delay': None, 'start': None, 'goal': None},
    {'delay': None, 'start': None, 'goal': None},
    {'delay': None, 'start': None, 'goal': None},
]
OUTPUT_SETTING = {
    '信号': True,
    '開始': True,
    '接続': True,
    '進入': True,
    '通過': True,
    '到着': True,
    'ALL': True
}


# 以下システム用

pid = str(random.randint(0, 10000)).zfill(5)
table_name = f'control{pid}'
args = sys.argv
start_time = None
arrived_num = 0
blue_traffic_light = 0
switch_traffic_light_time = 0
is_yellow = False
is_stop_control = False


if 'lr' in args:
    r = str(random.randint(0, 10000))
    LOG_FILE_PATH += f'_{r.zfill(5)}.log'
else:
    LOG_FILE_PATH += f'.log'
print(f'pid {pid}')


class Communication():
    def __init__(self):
        self.connect_clients = []
        self.entry_clients = []

    def add_connect(self, car_id, start, goal):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()

        dest = (goal+4 - start) % 4
        cur.execute(f'''
            INSERT INTO {table_name} VALUES (
            "{car_id}", {start}, {dest}, "connect", {time.time()-start_time}
        )''')
        dist = ['北', '東', '南', '西']
        cprint(car_id, '接続', f'{start} -> {goal}')

    def add_entry(self, car_id, delay):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()
        self.entry_clients.append(car_id)
        cur.execute(
            f'UPDATE {table_name} SET status="entry" WHERE car_id="{car_id}"')

        cprint(car_id, '進入')
        time.sleep(delay)

    def add_passed(self, car_id):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()
        cur.execute(f'DELETE FROM {table_name} WHERE car_id="{car_id}"')
        cprint(car_id, '通過')


def cprint(car_id, status, data=''):
    if status in OUTPUT_SETTING and OUTPUT_SETTING[status] and OUTPUT_SETTING['ALL']:
        if status == '信号':
            print(f'{(time.time()-start_time):.3} {status}: {data}')
        else:
            print(f'{(time.time()-start_time):.3} {car_id}: {status} {data}')

        with open(LOG_FILE_PATH, 'a') as f:
            if status == '信号':
                f.write(f'{(time.time()-start_time):.3} {status}: {data}\n')
            else:
                f.write(
                    f'{(time.time()-start_time):.3} {car_id}: {status} {data}\n')


comms = Communication()
