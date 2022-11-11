import sqlite3
import time


# 処理の遅延
PROCESS_DELAY = 0.1
# 車の速さ
CAR_SPEED = 50
# 前方の車1台あたりの遅延
ENTRY_DELAY = 0.5
# 交差点を通過するまでの時間
CAR_PASSED_TIME = 5
# 信号機の時間
TRAFFIC_LIGHT_TIME = [10, 10, 10, 10]
# データベースのパス
DB_PATH = '../db/simulator.db'
# クライアントの時間差をランダムにした時の範囲
time_range = (0, 10)
# クライアントデータ　
clients = [
    # 前の車との出発時間の差
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
    {'time': 0, 'start_node': None, 'goal_node': None},
]


# 以下システム用

start_time = None
arrived_num = 0
clients_data = {}
is_stop_control = False


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
        dest = cur.fetchone()[0]
        cur.execute(f'''
            REPLACE INTO control VALUES (
            "{car_id}", "{now_cross}", {origin}, {dest}, "connect", {time.time()-start_time}
        )''')
        print(f'{car_id}: 接続 {now_cross}')

    def add_entry(self, car_id):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()
        self.entry_clients.append(car_id)
        cur.execute(
            f'UPDATE control SET status="entry" WHERE car_id="{car_id}"')

        print(f'{car_id}: 進入')

    def add_passed(self, car_id):
        conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
        cur = conn.cursor()
        self.passed_clients.append(car_id)
        self.client_data[car_id]['data'].pop(0)
        cur.execute(f'DELETE FROM control WHERE car_id="{car_id}"')
        print(f'{car_id}: 通過')

    def add_client_data(self, car_id, data):
        self.client_data[car_id] = {
            'status': 'connect',
            'data': data
        }

    def get_client_data(self, car_id):
        return self.client_data[car_id]['data']
    
    def get_next_cross_data(self, car_id):
        return self.client_data[car_id]['data'][0]

comms = Communication()