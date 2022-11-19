import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import config as cf
import client as cl


def decide_can_entry(my_data, entry_list):
    can_entry = True
    for you_data in entry_list:
        if my_data[2] == you_data[2]:
            can_entry = True

        elif (my_data[2] + my_data[3]) % 4 == (you_data[2] + you_data[3]) % 4:
            can_entry = False

        elif my_data[3] == 1:
            can_entry = True

        elif my_data[3] == 2:
            can_entry = True
            my_left = (my_data[2] + 1) % 4
            you_dest_dir = (you_data[2] + you_data[3]) % 4

            if (you_data[2] == my_left) or (you_dest_dir == my_left):
                can_entry = False

        elif my_data[3] == 3:
            can_entry = False

            judge_1 = you_data[2] == (my_data[2] + 1) % 4   # 相手が左から来るか
            judge_2 = you_data[3] == (my_data[2] + 2) % 4   # 相手が前に行くか
            if judge_1 and judge_2:
                can_entry = True

            judge_1 = you_data[2] == (my_data[2] + 2) % 4   # 相手が前から来るか
            judge_2 = (you_data[2] + you_data[3]
                       ) % 4 == (my_data[2] + 1) % 4   # 相手が左に行くか
            if judge_1 and judge_2:
                can_entry = True

            judge_1 = you_data[2] == (my_data[2] + 3) % 4   # 相手が右から来るか
            judge_2 = (you_data[2] + you_data[3]
                       ) % 4 == my_data[2]   # 相手が自分側に行くか
            if judge_1 and judge_2:
                can_entry = True

        else:
            cf.cprint('その他', f'未実装だわぼけ！ {my_data}')

        if not can_entry:
            break

    return can_entry


def check_can_entry(cross_name):
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM control WHERE cross="{cross_name}" AND pid="{cf.pid}" ORDER BY time ASC')
    control_data = cur.fetchall()

    entry_list = [c for c in control_data if c[4] == 'entry']
    check_list = [c for c in control_data if c[4] != 'entry']
    wait_cars = [0, 0, 0, 0]
    wait_lane = []

    executor = ThreadPoolExecutor()
    for my_data in check_list:
        if my_data[2] in wait_lane:
            continue
        can_entry = decide_can_entry(my_data, entry_list)

        if can_entry:
            cur.execute(
                f'UPDATE control SET status="entry" WHERE car_id="{my_data[0]}" AND pid="{cf.pid}"'
            )
            executor.submit(
                cl.cross_process,
                my_data[0],
                wait_cars[my_data[2]]
            )
            entry_list.append(my_data)
            wait_cars[my_data[2]] += 1
        else:
            wait_lane.append(my_data[2])


def control_traffic_light(cross):
    # 信号が黄色のとき
    if cf.is_yellow:
        elapsed_time = time.time() - cf.switch_traffic_light_time
        setting_time = cf.TRAFFIC_LIGHT_TIME_YELLOW
        if elapsed_time >= setting_time:
            cf.blue_traffic_light = (cf.blue_traffic_light + 1) % 2
            cf.is_yellow = False
            cf.cprint(
                '信号',
                f'信号 : --- 青 --- ({cf.blue_traffic_light}, {cf.blue_traffic_light+2})'
            )
        else:
            return

    # 信号が黄色ではないとき
    elapsed_time = time.time() - cf.switch_traffic_light_time
    setting_time = cf.TRAFFIC_LIGHT_TIME[cf.blue_traffic_light]
    diff_time = setting_time - elapsed_time
    if diff_time <= 0:
        cf.switch_traffic_light_time = time.time()
        cf.is_yellow = True
        cf.entry_num_list = {}
        cf.cprint('信号', '信号 : --- 黄 ---')

    if cross not in cf.entry_num_list:
        cf.entry_num_list[cross] = [0, 0, 0, 0]
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM control WHERE cross="{cross}" AND pid="{cf.pid}" ORDER BY time ASC')
    control_data = cur.fetchall()

    entry_list = [c for c in control_data if c[4] == 'entry']
    check_list = [c for c in control_data if c[4] != 'entry']
    wait_cars = [0, 0, 0, 0]
    stop_lane = [cf.blue_traffic_light+1, (cf.blue_traffic_light+3) % 4]

    executor = ThreadPoolExecutor()
    for my_data in check_list:
        if len(stop_lane) >= 4:
            return
        elif my_data[2] in stop_lane:
            continue
        elif diff_time < wait_cars[my_data[2]] * cf.ENTRY_DELAY:
            stop_lane.append(my_data[2])
            continue
        elif cf.entry_num_list[cross][my_data[2]] > cf.CAN_ENTRY_NUM[cf.blue_traffic_light]:
            stop_lane.append(my_data[2])
            continue

        if decide_can_entry(my_data, entry_list):
            cur.execute(
                f'UPDATE control SET status="entry" WHERE car_id="{my_data[0]}" AND pid="{cf.pid}"'
            )
            entry_list.append(my_data)
            executor.submit(
                cl.cross_process,
                my_data[0],
                wait_cars[my_data[2]]
            )
            cf.entry_num_list[cross][my_data[2]] += 1
        wait_cars[my_data[2]] += 1


def control():
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute(f'DELETE FROM control WHERE pid="{cf.pid}"')
    cur.execute(f'DELETE FROM cross_schedule WHERE pid="{cf.pid}"')

    executor = ThreadPoolExecutor()
    while True:
        if cf.is_stop_control:
            break
        cur.execute(f'SELECT cross FROM control WHERE pid="{cf.pid}"')
        crosses = [c[0] for c in cur.fetchall()]
        crosses = set(crosses)

        futures = []
        executor = ThreadPoolExecutor()
        for cross in crosses:
            if 'traficc-light' in cf.args:
                futures.append(executor.submit(control_traffic_light, cross))
            else:
                futures.append(executor.submit(check_can_entry, cross))

        for future in futures:
            future.result()

        time.sleep(cf.PROCESS_DELAY)


if __name__ == '__main__':
    main()
