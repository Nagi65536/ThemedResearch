import copy
from concurrent.futures import ThreadPoolExecutor
import random
import sqlite3
import time

import client as cl
import control as cr
import config as cf


def clients_init():
    global clients, start_time

    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT cross_1 FROM road_info')
    node_list = [c[0] for c in cur.fetchall()]

    for i, client in enumerate(cf.clients):
        tmp_node_list = copy.deepcopy(node_list)
        if client['time'] == None:
            client['time'] = random.randint(cf.time_range[0], cf.time_range[1])
        if not client['start_node']:
            client['start_node'] = random.choice(tmp_node_list)
            tmp_node_list.remove(client['start_node'])
        if not client['goal_node']:
            client['goal_node'] = random.choice(tmp_node_list)
        cf.clients[i] = client


def main():
    cf.start_time = time.time()
    clients_init()
    futures = []

    with ThreadPoolExecutor() as executor:
        future = executor.submit(cr.control)

        for i, client in enumerate(cf.clients):
            # 車の接続開
            car_id = f'car_{str(i).zfill(3)}'
            start_node = client['start_node']
            goal_node = client['goal_node']
            executor.submit(
                cl.communicate, car_id, start_node, goal_node)

            # 次の車の発車時間まで待機
            if len(cf.clients) > i+1:
                time.sleep(cf.clients[i]['time'])
        
        future.result()
        print()
        print(f'経過時間 {time.time() - cf.start_time}')
                

if __name__ == '__main__':
    main()
