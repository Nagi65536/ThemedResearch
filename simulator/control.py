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
            print(f'{my_data[0]}: 未実装だわぼけ！ {my_data}')

        if not can_entry:
            break

    return can_entry


def check_can_entry(cross_name):
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM control WHERE cross = "{cross_name}" ORDER BY time ASC')
    control_data = cur.fetchall()

    entry_list = [c for c in control_data if c[4] == 'entry']
    check_list = [c for c in control_data if c[4] != 'entry']
    wait_cars = [0, 0, 0, 0]

    executor = ThreadPoolExecutor()
    for my_data in check_list:
        can_entry = decide_can_entry(my_data, entry_list)

        if can_entry:
            executor.submit(cl.cross_process, my_data[0], wait_cars[my_data[2]])
            wait_cars[my_data[2]] += 1


def control():
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute('DELETE FROM control')

    while True:
        if cf.is_stop_control:
            break
        cur.execute('SELECT cross FROM control')
        crosses = [c[0] for c in cur.fetchall()]
        crosses = set(crosses)

        for cross in crosses:
            check_can_entry(cross)

        time.sleep(cf.PROCESS_DELAY)


if __name__ == '__main__':
    main()
