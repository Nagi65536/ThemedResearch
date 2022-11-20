import sqlite3
import sys
import time
import random


# ログファイルをランダムにする
# 引数 log-random
# 制御方法を信号にする
# 引数 traficc-light
# 回避しない
# 引数 not-avoidance
# ログを取る
# 引数 log


# ログファイルのパス
LOG_FILE_PATH = f'./log/simulator-2timer'
# データベースのパス
DB_PATH = './db/simulator2-timer'
# マップの大きさ
MAP_SIZE = 12
# 処理の遅延
PROCESS_DELAY = 0.1
# 車の速さ
CAR_SPEED = 10
# 交差点混雑度を検索する時間範囲
CHECK_CONGESTION_RANGE = (-10, 5)
# 混雑と判断されない車の最大数
CONFLICT_NUM = 5
# 交差点到着予定時間を出す上での1台あたりの遅延
ARRIVAL_DELAY = 0.5
# 待機中の前方の車1台あたりの遅延(待機位置から交差点進入まで)
ENTRY_DELAY = 0.5
# 交差点を通過するまでの時間
CAR_PASSED_TIME = 2
# 信号機の時間
TRAFFIC_LIGHT_TIME = (20, 20)
# 黄色信号の時間
TRAFFIC_LIGHT_TIME_YELLOW = 5
# 1ターンに1方向から進入できる車の最大数
CAN_ENTRY_NUM = (10, 10)
# クライアントの時間差をランダムにした時の範囲(ms)
TIME_RANDOM_RANGE = [2000, 2000]

LOOP_NUM = 120
TIMER = 60 * 5
OUTPUT_SETTING = {
    '信号': True,
    '開始': False,
    '探索': False,
    '経路': False,
    '回避': False,
    '接続': True,
    '進入': True,
    '通過': True,
    '移動': False,
    '到着': True,
    '失敗': False,
    '状況': True,
    'その他': True,
}


# 以下システム用

pid = str(random.randint(0, 10000)).zfill(5)
start_time = 0
arrived_num = 0
departed_num = 0
is_stop_control = False
args = sys.argv
is_yellow = False
blue_traffic_light = 0
switch_traffic_light_time = 0
entry_num_list = {}

DB_PATH += f'_{pid}.db'
if 'traficc-light' in args:
    LOG_FILE_PATH += '_tf'
else:
    LOG_FILE_PATH += '_new'
if 'not-avoidance' in args:
    LOG_FILE_PATH += '_not.log'
else:
    LOG_FILE_PATH += '_avd.log'

print()
print(f'ログファイル {LOG_FILE_PATH}')
print(f'pid {pid}')


class Communication():
    def __init__(self):
        self.connect_clients = []
        self.entry_clients = []
        self.passed_clients = []
        self.client_data = {}

    def add_connect(self, car_id):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()

        route = [d[0] for d in self.client_data[car_id]['data']]
        origin_cross = route[0]
        now_cross = route[1]
        dest_cross = route[2]

        self.connect_clients.append(car_id)

        # 来る方角を取得
        cur.execute(f'''
            SELECT direction FROM road_info
            WHERE cross_1="{now_cross}" AND cross_2="{origin_cross}"
        ''')
        origin = cur.fetchone()[0]

        # 行く方角を取得
        cur.execute(f'''
            SELECT direction FROM road_info
            WHERE cross_1="{now_cross}" AND cross_2="{dest_cross}"
        ''')
        dest = (cur.fetchone()[0] - origin + 4)%4

        cur.execute(f'''
            INSERT INTO control VALUES (
            "{car_id}", "{now_cross}", {origin}, {dest}, "connect", {time.time()-start_time}, "{pid}"
        )''')
        cprint('接続', f'{car_id} : 接続 {now_cross}')

    def add_entry(self, car_id):
        self.entry_clients.append(car_id)
        cprint('進入', f'{car_id} : 進入')

    def add_passed(self, car_id):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()
        self.passed_clients.append(car_id)
        self.client_data[car_id]['data'].pop(0)
        cur.execute(
            f'DELETE FROM control WHERE car_id="{car_id}" AND pid="{pid}"')
        cprint('通過', f'{car_id} : 通過')
        cur.execute(f'''
        SELECT car_id FROM control WHERE
        status="connect" AND
        pid="{pid}"
        ''')
        global arrived_num
        cprint('状況', f'処理数 : {arrived_num}  待機数 : {len(cur.fetchall())}')

    def add_client_data(self, car_id, data):
        self.client_data[car_id] = {
            'status': 'connect',
            'data': data
        }

    def get_client_data(self, car_id):
        return self.client_data[car_id]['data']

    def get_next_cross_data(self, car_id):
        return self.client_data[car_id]['data'][0]


def cprint(type_, data):
    if is_stop_control:
        return

    if not (type_ in OUTPUT_SETTING and OUTPUT_SETTING[type_]):
        return

    time_ = int(time.time()-start_time)
    print(f'{time_} {data}')

    if 'log' in args:
        with open(LOG_FILE_PATH, 'a') as f:
            f.write(f'{time_} {data}\n')


def config_init():
    global start_time, arrived_num, departed_num, is_stop_control
    global args, is_yellow, blue_traffic_light, switch_traffic_light_time

    start_time = None
    arrived_num = 0
    departed_num = 0
    is_stop_control = False
    is_yellow = False
    blue_traffic_light = 0
    switch_traffic_light_time = 0

    TIME_RANDOM_RANGE[0] += 100
    TIME_RANDOM_RANGE[1] += 100


comms = Communication()
