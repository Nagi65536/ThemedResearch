import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import config as cf
import client as cl


def decide_can_entry(my_data, check_list):
    can_entry = True
    for you_data in check_list:
        if my_data[1] == you_data[1]:
            can_entry = True

        elif (my_data[1] + my_data[2]) % 4 == (you_data[1] + you_data[2]) % 4:
            can_entry = False

        elif my_data[2] == 1:
            can_entry = True

        elif my_data[2] == 2:
            my_left = (my_data[1] + 1) % 4
            you_dest_dir = (you_data[1] + you_data[2]) % 4

            if (you_data[1] == my_left) or (you_dest_dir == my_left):
                can_entry = False

        elif my_data[2] == 3:
            can_entry = False

            judge_1 = you_data[1] == (my_data[1] + 1) % 4   # 相手が左から来るか
            judge_2 = you_data[2] == (my_data[1] + 2) % 4   # 相手が前に行くか
            if judge_1 and judge_2:
                can_entry = True

            judge_1 = you_data[1] == (my_data[1] + 2) % 4   # 相手が前から来るか
            judge_2 = (you_data[1] + you_data[2]
                       ) % 4 == (my_data[1] + 1) % 4   # 相手が左に行くか
            if judge_1 and judge_2:
                can_entry = True

            judge_1 = you_data[1] == (my_data[1] + 3) % 4   # 相手が右から来るか
            judge_2 = (you_data[1] + you_data[1]
                       ) % 4 == my_data[1]   # 相手が自分側に行くか
            if judge_1 and judge_2:
                can_entry = True

        else:
            print(
                f'{my_data[0]}: 未実装だわぼけ！ {my_data[1]}-{my_data[2]} {you_data[1]}-{you_data[2]}')

        if not can_entry:
            break

    return can_entry


def check_can_entry():
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(f'SELECT * FROM control ORDER BY time ASC')
    control_data = cur.fetchall()

    entry_list = [c for c in control_data if c[3] == 'entry']
    check_list = [c for c in control_data if c[3] != 'entry']
    wait_cars = [0, 0, 0, 0]

    executor = ThreadPoolExecutor()
    for my_data in check_list:
        can_entry = decide_can_entry(my_data, entry_list)

        if can_entry:
            cl.cross_process(my_data[0], wait_cars[my_data[1]])
            wait_cars[my_data[1]] += 1


def control_traffic_light():
    # 信号が黄色のとき
    if cf.is_yellow:
        time_1 = time.time() - cf.switch_traffic_light_time
        time_2 = cf.TRAFFIC_LIGHT_TIME_YELLOW

        if time_1 >= time_2:
            cf.blue_traffic_light = (cf.blue_traffic_light + 1) % 2
            cf.is_yellow = False
            cf.cprint(
                '', '信号', f'青 ({cf.blue_traffic_light}, {cf.blue_traffic_light+2})')
        else:
            return
    # 信号が黄色ではないとき
    else:
        time_1 = time.time() - cf.switch_traffic_light_time
        time_2 = cf.TRAFFIC_LIGHT_TIME[cf.blue_traffic_light]
        if time_1 >= time_2:
            cf.switch_traffic_light_time = time.time()
            cf.is_yellow = True
            cf.cprint('', '信号', '黄')

    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(f'SELECT * FROM control ORDER BY time ASC')
    control_data = cur.fetchall()

    entry_list = [c for c in control_data if c[3] == 'entry']
    check_list = [c for c in control_data if c[3] != 'entry']
    wait_cars = [0, 0, 0, 0]
    stop_lane = []

    executor = ThreadPoolExecutor()
    for my_data in check_list:
        blue = (cf.blue_traffic_light, cf.blue_traffic_light+2)
        if my_data[1] not in stop_lane \
                and my_data[1] in blue:

            can_entry = decide_can_entry(my_data, entry_list)
            if can_entry:
                entry_list.append(my_data)
                executor.submit(
                    cl.cross_process,
                    my_data[0], wait_cars[my_data[1]]
                )
                wait_cars[my_data[1]] += 1
            else:
                stop_lane.append(my_data[1])


def control_down_grade():
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    print('ok')
    cur.execute(f'SELECT * FROM control ORDER BY time ASC')
    control_data = cur.fetchall()
    status_list = [c[3] for c in control_data if c[3] == 'entry']

    if 'entry' not in status_list:
        executor = ThreadPoolExecutor()
        cl.cross_process(control_data[0][0])


def control():
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('DELETE FROM control')
    cf.switch_traffic_light_time = time.time()

    while True:
        if cf.is_stop_control:
            break
        if 'tl' in cf.args:
            control_traffic_light()
        elif 'dg' in cf.args:
            control_down_grade()
        else:
            check_can_entry()

        time.sleep(cf.PROCESS_DELAY)
