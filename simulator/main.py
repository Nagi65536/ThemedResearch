import copy
from concurrent.futures import ThreadPoolExecutor
import random
import sqlite3
import time
from astar import a_star


# 車の速さ
CAR_SPEED = 10
# 処理の遅延
PROCESS_DELAY = 0.1
# 交差点を通過するまでの時間
CAR_PASSED_TIME = 2
# 信号機の時間
TRAFFIC_LIGHT_TIME = [10, 10, 10, 10]
# データベースのパス
DB_PATH = '../db/simulator.db'
# クライアントデータ　
clients = [
    {'start_time': 0, 'start_node': None, 'goal_node': None},
]


class Communication():
    def __init__(self):
        self.connect_clients = []
        self.entry_clients = []
        self.passed_clients = []
        self.client_data = {}

    def add_connect(self, car_id):
        print('ok')
        global start_time
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
        self.client_data.pop(car_id)
        cur.execute(f'DELETE FROM control WHERE car_id="{car_id}"')
        print(f'{car_id}: 通過')

    def add_client_data(self, car_id, data):
        self.client_data[car_id] = {
            'status': 'connect',
            'data': data
        }


# サーバー
def check_can_entry(cross_name):
    conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM control WHERE cross = "{cross_name}" ORDER BY time ASC')
    control_data = cur.fetchall()

    entry_list = [c for c in control_data if c[4] == 'entry']
    check_list = [c for c in control_data if c[4] != 'entry']

    executor = ThreadPoolExecutor()
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
            executor.submit(cross_process, my_data[0])


def control():
    conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('DELETE FROM control')

    while True:
        cur.execute('SELECT cross FROM control')
        crosses = [c[0] for c in cur.fetchall()]
        crosses = set(crosses)

        for cross in crosses:
            check_can_entry(cross)

        time.sleep(PROCESS_DELAY)


# クライアント

def communicate(car_id, start_node, goal_node, delay=-1):
    print(f'{car_id}: 探索 {start_node} -> {goal_node}')
    data = a_star(start_node, goal_node)
    comms.add_client_data(car_id, data)

    if data and len(data) >= 3:
        comms.add_connect(car_id)
    else:
        print(f'{car_id}: 目的地到着')


def cross_process(car_id):
    # 交差点進入
    comms.add_entry(car_id)
    time.sleep(CAR_PASSED_TIME)

    # 交差点通過
    comms.add_passed(car_id)
    data = comms.client_data
    print('data', data)

    wait_time = data['data'][0][1] / CAR_SPEED
    print(wait_time)
    time.sleep(wait_time)
    print(comms.client_data)
    if len(comms[car_id]['data']) >= 3:
        print('a')
        comms.add_connect(car_id)
    else:
        print(f'{car_id}: 目的地到着')


def clients_init():
    global clients, start_time

    conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT cross_1 FROM road_info')
    node_list = [c[0] for c in cur.fetchall()]

    for i, client in enumerate(clients):
        tmp_node_list = copy.deepcopy(node_list)
        if client['start_time'] == None:
            client['start_time'] = random.randint(0, 10)
        if not client['start_node']:
            client['start_node'] = random.choice(tmp_node_list)
            tmp_node_list.remove(client['start_node'])
        if not client['goal_node']:
            client['goal_node'] = random.choice(tmp_node_list)
        clients[i] = client

    clients = sorted(clients, key=lambda x: x['start_time'])


# メイン

def main():
    global clients

    clients_init()
    futures = []

    with ThreadPoolExecutor() as executor:
        future = executor.submit(control)
        futures.append(future)
        for i, client in enumerate(clients):
            # 車の接続開始
            car_id = f'car_{str(i).zfill(3)}'
            start_node = client['start_node']
            goal_node = client['goal_node']
            future = executor.submit(
                communicate, car_id, start_node, goal_node)
            futures.append(future)

            # 次の車の発車時間まで待機
            if len(clients) > i+1:
                time.sleep(
                    clients[i+1]['start_time'] - client['start_time'])

    for future in futures:
        print(future.result())


if __name__ == '__main__':
    start_time = time.time()
    # clients_data = {}
    comms = Communication()
    main()
