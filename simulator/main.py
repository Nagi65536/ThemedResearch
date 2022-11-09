import random
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

from astar import a_star
import client as cl
import control as cr
import config as cf


def clients_random_setting():
    conn = sqlite3.connect(f'{DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT cross_1 from crosses_info')
    node_list = [c[0] for c in cur.fetchall()]

    for client in cf.clients:
        tmp_node_list = copy.deepcopy(node_list)
        if client['start_time'] == None:
            client['start_time'] = random.randint(0, 10)
        if not client['start_node']:
            client['start_node'] = random.choice(tmp_node_list)
            tmp_node_list.remove(client['start_node'])
        if not client['goal_node']:
            client['goal_node'] = random.choice(tmp_node_list)


def main():
    global start_time
    clients_random_setting()

    cf.clients
    cf.start_time = time.time()

    # クライアントを発車時間順に並び替え
    cf.clients = sorted(cf.clients, key=lambda x: x['start_time'])
    executor.submit(cr.control)
    with ThreadPoolExecutor() as executor:
        for i, client in enumerate(cf.clients):
            # 車の接続開始
            executor.submit(
                cl.communication, f'car_{str(i).zfill(3)}', client['start_node'], client['goal_node'])

            # 次の車の発車時間まで待機
            if len(cf.clients) > i+1:
                time.sleep(
                    cf.clients[i+1]['start_time'] - client['start_time'])


if __name__ == '__main__':
    main()
