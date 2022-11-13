import copy
from concurrent.futures import ThreadPoolExecutor
import random
import sqlite3
import time

import client as cl
import control as cr
import config as cf


def log_init():
    with open(cf.LOG_FILE_PATH, 'a') as f:
        f.write(f'''PROCESS_DELAY: {cf.PROCESS_DELAY}
CAR_SPEED    : {cf.CAR_SPEED}
CHECK_CONGESTION_RANGE: {cf.CHECK_CONGESTION_RANGE}
CONFLICT_NUM : {cf.CONFLICT_NUM}
ARRIVAL_DELAY: {cf.ARRIVAL_DELAY}
ENTRY_DELAY  : {cf.ENTRY_DELAY}
CAR_PASSED_TIME   : {cf.CAR_PASSED_TIME}
TRAFFIC_LIGHT_TIME: {cf.TRAFFIC_LIGHT_TIME}
TIME_RANDOM_RANGE : {cf.TIME_RANDOM_RANGE}
''')
        f.write('clients\n')
        f.write(str(cf.clients).replace("},", "},\n"))
        f.write('\n\n')


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
                time.sleep(cf.clients[i+1]['delay'])

        future.result()
        print()
        print(f'経過時間 {time.time() - cf.start_time}')


if __name__ == '__main__':
    main()
