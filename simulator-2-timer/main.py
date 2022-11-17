import copy
import random
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import client as cl
import config as cf
import control as cr


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
            cf.is_stop_control = True
            print(f'\n処理数 {cf.arrived_num}\n')
            with open(cf.LOG_FILE_PATH, 'a') as f:
                f.write(f'\n処理数 {cf.arrived_num}\n')
            return

        time.sleep(cf.PROCESS_DELAY)


def main():
    log_init()
    cf.start_time = time.time()
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('SELECT cross FROM cross_position')
    crosses = list(set([c[0] for c in cur.fetchall()]))

    with ThreadPoolExecutor() as executor:
        future = executor.submit(cr.control)
        executor.submit(timer)
        while True:
            if cf.is_stop_control:
                break

            nodes = random.sample(crosses, 2)
            car_id = f'car_{str(cf.departed_num).zfill(3)}'
            cf.cprint(
                car_id,
                '開始',
                f'{(time.time()-cf.start_time):.3} s  {nodes[0]} -> {nodes[1]}'
            )
            cf.departed_num += 1
            executor.submit(
                cl.communicate, car_id, nodes[0], nodes[1])

            sleep = random.randint(
                cf.TIME_RANDOM_RANGE[0],
                cf.TIME_RANDOM_RANGE[1]
            ) / 1000
            time.sleep(sleep)


if __name__ == '__main__':
    main()
