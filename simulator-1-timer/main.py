import copy
from concurrent.futures import ThreadPoolExecutor
import random
import sqlite3
import time

import client as cl
import control as cr
import config as cf
from setting import db_init


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


def main():
    db_init(cf.table_name)

    cf.start_time = time.time()
    futures = []

    with ThreadPoolExecutor() as executor:
        executor.submit(cr.control)

        while True:
            if cf.is_stop_control:
                break

            car_id = f'car_{str(cf.departed_num).zfill(3)}'
            p = random.sample([0, 1, 2, 3], 2)
            time_ = time.time() - cf.start_time
            cf.cprint(car_id, '開始', f'{time_:.3} s  {p[0]} -> {p[1]}')
            executor.submit(cl.communicate, car_id, p[0], p[1])
            cf.departed_num += 1

            # 次の車の発車時間まで待機
            sleep = random.randint(cf.DELAY_RANGE[0], cf.DELAY_RANGE[1])
            time.sleep(sleep)


if __name__ == '__main__':
    main()
