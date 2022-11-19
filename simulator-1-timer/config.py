import sqlite3
import sys
import time
import random


# 信号機モード
# 引数 tl
# グレードダウンモード
# 引数 gd
# ログあり
# 引数 log
# ログファイルをランダムに
# lr


# ログファイルのパス
LOG_FILE_PATH = f'./log/simulator-1timer'
# データベースのパス
DB_PATH = './db/simulator-1timer.db'
# 処理の遅延
PROCESS_DELAY = 0.1
# 待機中の前方の車1台あたりの遅延(待機位置から交差点進入まで)
ENTRY_DELAY = 0.5
# 交差点を通過するまでの時間
CAR_PASSED_TIME = 2
# 信号機の時間(南北, 東西)
TRAFFIC_LIGHT_TIME = (10, 10)
# 1ターンに1方向から進入できる車の最大数
CAN_ENTRY_NUM = (TRAFFIC_LIGHT_TIME[0]/0.7, TRAFFIC_LIGHT_TIME[1]/0.7)
# 黄色の時間
TRAFFIC_LIGHT_TIME_YELLOW = 2

# ループ回数
LOOP_NUM = 3
# 計測時間(s)
TIMER = 10
# クライアントの時間差をランダムにした時の範囲(ms)
DELAY_RANGE = (1000, 1000)
# 出力内容
OUTPUT_SETTING = {
    '信号': True,
    '開始': False,
    '接続': True,
    '進入': True,
    '通過': False,
    '到着': False,
    'その他': True
}


# 以下システム用

pid = str(random.randint(0, 10000)).zfill(5)
table_name = f'control{pid}'
args = sys.argv
start_time = None
departed_num = 0
arrived_num = 0
blue_traffic_light = 0
switch_traffic_light_time = 0
is_yellow = False
is_stop_control = False
entry_num_list = [0, 0, 0, 0]


if 'lr' in args:
    LOG_FILE_PATH += f'_{pid}.log'
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

        dest = (goal - start + 4) % 4
        cur.execute(f'''
            INSERT INTO {table_name} VALUES (
            "{car_id}", {start}, {dest}, "connect", {time.time()-start_time}
        )''')
        dist = ['北', '東', '南', '西']
        cprint('接続', f'{car_id} : 接続 {start} -> {goal}')

    def add_entry(self, car_id, delay):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()
        self.entry_clients.append(car_id)
        cur.execute(
            f'UPDATE {table_name} SET status="entry" WHERE car_id="{car_id}"')

        cprint('進入', f'{car_id} : 進入')
        time.sleep(delay)

    def add_passed(self, car_id):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()
        cur.execute(f'DELETE FROM {table_name} WHERE car_id="{car_id}"')
        cprint('通過', f'{car_id} : 通過')

        cur.execute(f'''
        SELECT car_id FROM {table_name} WHERE
        status="connect"
        ''')
        cprint('その他', f'待機数 {len(cur.fetchall())} 処理数 {arrived_num}')


def cprint(type_, data):
    if type_ in OUTPUT_SETTING and OUTPUT_SETTING[type_]:
        time_ = int(time.time() - start_time)
        print(f'{time_} {data}')

        if 'log' in args:
            with open(LOG_FILE_PATH, 'a') as f:
                f.write(f'{time_} {data}\n')


def config_init():
    global start_time, departed_num, arrived_num, blue_traffic_light
    global switch_traffic_light_time, is_yellow, is_stop_control

    start_time = None
    departed_num = 0
    arrived_num = 0
    blue_traffic_light = 0
    switch_traffic_light_time = 0
    is_yellow = False
    is_stop_control = False


comms = Communication()
