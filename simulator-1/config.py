import sqlite3
import sys
import time


# ログファイルのパス
LOG_FILE_PATH = f'../log/simulator-1.log'
# データベースのパス
DB_PATH = '../db/simulator1.db'
# 処理の遅延
PROCESS_DELAY = 0.1
# 前方の車1台あたりの遅延
ENTRY_DELAY = 0.5
# 交差点を通過するまでの時間
CAR_PASSED_TIME = 5
# 信号機の時間(南北, 東西)
TRAFFIC_LIGHT_TIME = (4, 4)
# 黄色の時間
TRAFFIC_LIGHT_TIME_YELLOW = 2
# クライアントの時間差をランダムにした時の範囲
DELAY_RANGE = (0, 10)
# クライアントデータ
clients = [
    # 前の車との出発時間の差, スタート位置, ゴール位置
    {'delay': 0, 'start': 0, 'goal': 3},
    {'delay': 0, 'start': 2, 'goal': 0},
]
OUTPUT_SETTING = {
    '信号': True,
    '開始': False,
    '接続': True,
    '進入': True,
    '通過': True,
    '到着': True,
}


# 以下システム用

args = sys.argv
start_time = None
arrived_num = 0
blue_traffic_light = 0
switch_traffic_light_time = 0
is_yellow = False
is_stop_control = False


class Communication():
    def __init__(self):
        self.connect_clients = []
        self.entry_clients = []

    def add_connect(self, car_id, start, goal):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()

        dest = (goal+4 - start) % 4
        cur.execute(f'''
            REPLACE INTO control VALUES (
            "{car_id}", {start}, {dest}, "connect", {time.time()-start_time}
        )''')
        dist = ['北', '東', '南', '西']
        cprint(car_id, '接続', f'{start} -> {goal}')

    def add_entry(self, car_id, delay):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()
        self.entry_clients.append(car_id)
        cur.execute(
            f'UPDATE control SET status="entry" WHERE car_id="{car_id}"')

        cprint(car_id, '進入')
        time.sleep(delay)

    def add_passed(self, car_id):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()
        cur.execute(f'DELETE FROM control WHERE car_id="{car_id}"')
        cprint(car_id, '通過')


def cprint(car_id, status, data=''):
    if status in OUTPUT_SETTING and OUTPUT_SETTING[status]:
        if status == '信号':
            print(f'{status}: {data}')
        else:
            print(f'{car_id}: {status} {data}')

        with open(LOG_FILE_PATH, 'a') as f:
            if status == '信号':
                f.write(f'{status}: {data}\n')
            else:
                f.write(f'{car_id}: {status} {data}\n')


comms = Communication()
