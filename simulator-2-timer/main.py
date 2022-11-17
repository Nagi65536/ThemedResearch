import copy
import random
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import client as cl
import config as cf
import control as cr
from setting import generate_db, clear_db


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

    clear_db()
    cf.is_stop_control = True
    print(f'\n処理数 {cf.arrived_num}\n')
    with open(cf.LOG_FILE_PATH, 'a') as f:
        f.write(f'処理数 {cf.arrived_num}\n')


def normal():
    cf.config_init()
    generate_db()

    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('SELECT cross FROM cross_position')
    crosses = list(set([c[0] for c in cur.fetchall()]))

    cf.start_time = time.time()
    with ThreadPoolExecutor() as executor:
        future = executor.submit(cr.control)
        executor.submit(timer)
        while True:
            nodes = random.sample(crosses, 2)
            car_id = f'car_{str(cf.departed_num).zfill(3)}'
            cf.cprint(
                car_id,
                '開始',
                f'{(time.time()-cf.start_time):.3} s  {nodes[0]} -> {nodes[1]}'
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


def main():
    for i in range(1, cf.LOOP_NUM+1):
        print(f'----- {i}回目 -----')
        print()
        normal()


if __name__ == '__main__':
    main()
