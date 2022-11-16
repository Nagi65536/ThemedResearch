import copy
from concurrent.futures import ThreadPoolExecutor
import random
import sqlite3
import time

import client as cl
import control as cr
import config as cf
from setting import db_init, remove_table


def log_init():
    if cf.OUTPUT_SETTING['ALL']:
        return

    with open(cf.LOG_FILE_PATH, 'a') as f:
        mode = 'TL' if len(cf.args) > 1 and cf.args[1] == 'tl' else 'NEW'
        f.write(f'----  ---\n\
        PROCESS_DELAY: {cf.PROCESS_DELAY}\n\
        ENTRY_DELAY  : {cf.ENTRY_DELAY}\n\
        CAR_PASSED_TIME: {cf.CAR_PASSED_TIME}\n\
        TRAFFIC_LIGHT_TIME: {cf.TRAFFIC_LIGHT_TIME}\n\
        TRAFFIC_LIGHT_TIME_YELLOW: {cf.TRAFFIC_LIGHT_TIME_YELLOW}\n\
        DELAY_RANGE : {cf.DELAY_RANGE}\n')
        f.write('clients\n')
        f.write(str(cf.clients).replace("},", "},\n"))
        f.write('\n\n')


def clients_init():
    for i, client in enumerate(cf.clients):
        dir_list = [0, 1, 2, 3]
        if client['delay'] == None:
            client['delay'] = random.randint(cf.DELAY_RANGE[0], cf.DELAY_RANGE[1])
        if client['start'] == None:
            c = random.choice(dir_list)
            client['start'] = c
            dir_list.remove(c)
        if client['goal'] == None:
            client['goal'] = random.choice(dir_list)
        cf.clients[i] = client


def main():
    db_init(cf.table_name)

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
            cf.cprint(
                car_id,
                '開始',
                f'{(time.time()-cf.start_time):.3} s  {client["start"]} -> {client["goal"]}'
            )
            executor.submit(
                cl.communicate, car_id, start, goal)

            # 次の車の発車時間まで待機
            if len(cf.clients) > i+1:
                time.sleep(cf.clients[i+1]['delay'])

        future.result()
        print()
        print(f'経過時間 {time.time() - cf.start_time:.3}')
        with open(cf.LOG_FILE_PATH, 'a') as f:
            f.write(f'\n経過時間 {(time.time() - cf.start_time):.3} s\n\n')
        remove_table(cf.table_name)


if __name__ == '__main__':
    main()
