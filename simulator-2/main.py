import copy
import random
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import client as cl
import config as cf
import control as cr


def log_init():
    with open(cf.LOG_FILE_PATH, 'a') as f:
        mode = 'TL' if len(cf.args) > 1 and cf.args[1] == 'tl' else 'NEW'
        f.write(f'--- {mode} ---\n\
    PROCESS_DELAY: {cf.PROCESS_DELAY}\n\
    CAR_SPEED    : {cf.CAR_SPEED}\n\
    CHECK_CONGESTION_RANGE: {cf.CHECK_CONGESTION_RANGE}\n\
    CONFLICT_NUM : {cf.CONFLICT_NUM}\n\
    ARRIVAL_DELAY: {cf.ARRIVAL_DELAY}\n\
    ENTRY_DELAY  : {cf.ENTRY_DELAY}\n\
    CAR_PASSED_TIME   : {cf.CAR_PASSED_TIME}\n\
    TRAFFIC_LIGHT_TIME: {cf.TRAFFIC_LIGHT_TIME}\n\
    TIME_RANDOM_RANGE : {cf.TIME_RANDOM_RANGE}\n')
        f.write('clients\n')
        f.write(str(cf.clients).replace("},", "},\n"))
        f.write('\n\n')


def clients_init():
    global clients, start_time

    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT cross_1 FROM road_info')
    node_list = [c[0] for c in cur.fetchall()]

    for i, client in enumerate(cf.clients):
        tmp_node_list = copy.deepcopy(node_list)
        if client['time'] == None:
            client['time'] = random.randint(
                cf.TIME_RANDOM_RANGE[0],
                cf.TIME_RANDOM_RANGE[1]
            )
        if not client['start_node']:
            client['start_node'] = random.choice(tmp_node_list)
            tmp_node_list.remove(client['start_node'])
        if not client['goal_node']:
            client['goal_node'] = random.choice(tmp_node_list)
        cf.clients[i] = client


def main():
    log_init()
    cf.start_time = time.time()
    clients_init()

    with ThreadPoolExecutor() as executor:
        future = executor.submit(cr.control)
        for i, client in enumerate(cf.clients):
            # 車の接続開
            car_id = f'car_{str(i).zfill(3)}'
            cf.cprint(
                car_id,
                '開始',
                f'{(time.time()-cf.start_time):.3} s  {client["start_node"]}->{client["goal_node"]}'
            )
            start_node = client['start_node']
            goal_node = client['goal_node']
            executor.submit(
                cl.communicate, car_id, start_node, goal_node)

            # 次の車の発車時間まで待機
            if len(cf.clients) > i+1:
                time.sleep(cf.clients[i+1]['time'])

        future.result()
        print()
        print(f'経過時間 {(time.time() - cf.start_time):.3} s')
        with open(cf.LOG_FILE_PATH, 'a') as f:
            f.write(f'\n経過時間 {(time.time() - cf.start_time):.3} s\n\n\n')


if __name__ == '__main__':
    main()
