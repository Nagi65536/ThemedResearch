# 処理の遅延
PROCESS_DELAY = 0.1
# 信号機の時間
TRAFFIC_LIGHT_TIME = [10, 10, 10, 10]
# データベースのパス
DB_PATH = '../db/simulator.db'
# クライアントデータ　
clients = [
    {'start_time': 0, 'start_node': None, 'goal_node': None},
    {'start_time': 0, 'start_node': None, 'goal_node': None},
    {'start_time': 0, 'start_node': None, 'goal_node': None},
]

start_time = None


class Communication():
    def __init__(self):
        self.connect_clients = []
        self.entry_clients = []
        self.passed_clients = []

    def push_connect(self, car_id, origin_cross, destination_cross):
        self.connect_clients.append()