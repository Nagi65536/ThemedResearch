import copy
import random
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import client as cl
import config as cf
import control as cr
from setting import generate_db, clear_table


def log_init():
    if not cf.OUTPUT_SETTING['ALL']:
        return

    with open(cf.LOG_FILE_PATH, 'a') as f:
        mode = 'TRAFICC-LIGHT' if 'traficc-light' in cf.args else 'NEW'
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


def timer():
    while True:
        time_ = time.time() - cf.start_time
        if time_ > cf.TIMER:
            break
        time.sleep(cf.PROCESS_DELAY)

    cf.is_stop_control = True

    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(f'''
    SELECT car_id FROM control WHERE
    status="connect" AND
    pid="{cf.pid}"
    ''')
    wait_num = len(cur.fetchall())
    print(f'\n処理数 {cf.arrived_num}')
    print(f'待機数 {wait_num}')
    with open(cf.LOG_FILE_PATH, 'a') as f:
        f.write(f'処理数 {cf.arrived_num}  待機数 {wait_num}\n')
    time.sleep(10)
    clear_table(cf.DB_PATH)


def normal():
    cf.config_init()
    generate_db()

    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('SELECT cross FROM cross_position')
    crosses = list(set([c[0] for c in cur.fetchall()]))

    cf.start_time = time.time()
    with ThreadPoolExecutor() as executor:
        executor.submit(cr.control)
        future = executor.submit(timer)
        while True:
            nodes = random.sample(crosses, 2)
            car_id = f'car_{str(cf.departed_num).zfill(3)}'
            cf.cprint(
                '開始',
                f'{car_id} : 開始 {(time.time()-cf.start_time):.3} s  {nodes[0]} -> {nodes[1]}'
            )

            if cf.is_stop_control:
                break
            cf.departed_num += 1
            executor.submit(
                cl.communicate, car_id, nodes[0], nodes[1])

            sleep = random.randint(
                cf.TIME_RANDOM_RANGE[0],
                cf.TIME_RANDOM_RANGE[1]
            ) / 1000
            time.sleep(sleep)

        future.result()


def main():
    for i in range(1, cf.LOOP_NUM+1):
        cf.cprint('その他', f'----- {i}回目 -----\n')
        normal()


if __name__ == '__main__':
    main()
