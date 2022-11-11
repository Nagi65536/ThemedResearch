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

    for i, client in enumerate(cf.clients):
        if client['delay'] == None:
            client['delay'] = random.randint(cf.DELAY_RANGE[0], cf.DELAY_RANGE[1])
        if client['start'] == None:
            client['start'] = random.randint(0, 3)
        if client['goal'] == None:
            client['goal'] = random.randint(0, 3)
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
            start = client['start']
            goal = client['goal']
            executor.submit(
                cl.communicate, car_id, start, goal)

            # 次の車の発車時間まで待機
            if len(cf.clients) > i+1:
                time.sleep(cf.clients[i]['delay'])

        future.result()
        print()
        print(f'経過時間 {time.time() - cf.start_time}')


if __name__ == '__main__':
    main()
