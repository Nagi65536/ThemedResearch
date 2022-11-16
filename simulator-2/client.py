import sqlite3
import time

import config as cf
from config import comms
from astar import a_star


def communicate(car_id, start_node, goal_node, delay=-1):
    cf.cprint(car_id, '探索', f'{start_node} -> {goal_node}')
    disable_node = []

    while True:
        data = a_star(start_node, goal_node, disable_node)
        cf.cprint(car_id, '経路', f'{[d[0] for d in data]}')

        if not data:
            data = a_star(start_node, goal_node)
            if not data:
                cf.cprint(car_id, '失敗', '経路が見つかりませんでした')
                return
            break
        elif len(data) < 3:
            break

        congestion_node = congestion_check(car_id, data)
        if not congestion_node:
            break

        disable_node.append(congestion_node)
        cf.cprint(car_id, '回避', disable_node)

    comms.add_client_data(car_id, data)

    if data and len(data) >= 3:
        comms.add_connect(car_id)
    else:
        cf.arrived_num += 1
        cf.cprint(car_id, '到着', cf.arrived_num)
        if cf.arrived_num >= len(obj)(cf.clients):
            cf.is_stop_control = True


def congestion_check(car_id, data):
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    congestion = False
    cross_delay = 0
    for i, node in enumerate(data[1:-1]):
        arrival_time = time.time() + node[1]/cf.CAR_SPEED + cross_delay

        # 来る方角取得
        cur.execute(f'''
        SELECT direction FROM road_info WHERE
        cross_1="{data[i+1][0]}" AND
        cross_2="{data[i][0]}"
        ''')
        origin = cur.fetchone()[0]

        # 進行方向取得
        cur.execute(f'''
        SELECT direction FROM road_info WHERE
        cross_1="{data[i+1][0]}" AND
        cross_2="{data[i+2][0]}"
        ''')
        dest = (cur.fetchone()[0] + 4 - origin) % 4

        # 予定登録
        cur.execute(f'''
        INSERT INTO cross_schedule VALUES (
            "{car_id}", "{node[0]}", "{origin}", "{dest}", {arrival_time}, "{cf.pid}"
        )''')

        # 混雑度計算用データ取得
        cur.execute(f'''
        SELECT * FROM cross_schedule WHERE
        cross="{node[0]}" AND
        pid="{cf.pid}" AND
        time BETWEEN {arrival_time + cf.CHECK_CONGESTION_RANGE[0]} AND
        {arrival_time + arrival_time + cf.CHECK_CONGESTION_RANGE[1]}
        ''')
        cross_data = cur.fetchall()

        # 混雑か判断
        my_data = (car_id, node[0], origin, dest, arrival_time)
        is_conflict = decide_is_conflict(my_data, cross_data)

        if is_conflict:
            cur.execute(
                f'DELETE FROM cross_schedule WHERE car_id="{car_id}" AND pid="{cf.pid}"')
            return node[0]

    return None


def decide_is_conflict(my_data, cross_data):
    can_entry = True
    is_conflict = False
    conflict_num = 0
    car_num = [0, 0, 0, 0]

    for you_data in cross_data:
        car_num[you_data[2]] += 1
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

        if can_entry:
            conflict_num += 1

    if conflict_num > cf.CONFLICT_NUM:
        is_conflict = True
    elif car_num[my_data[2]] > cf.CONFLICT_NUM:
        is_conflict = True

    return is_conflict


def cross_process(car_id, front_cars=0):
    # 交差点進入
    comms.add_entry(car_id)
    time.sleep(front_cars * cf.ENTRY_DELAY)
    time.sleep(cf.CAR_PASSED_TIME)

    # 交差点通過
    comms.add_passed(car_id)
    dist = comms.get_next_cross_data(car_id)[1]
    wait_time = dist / cf.CAR_SPEED
    cf.cprint(car_id, '移動', f'{wait_time:3.3}s')
    time.sleep(wait_time)

    if len(comms.get_client_data(car_id)) >= 3:
        comms.add_connect(car_id)
    else:
        cf.arrived_num += 1
        cf.cprint(car_id, '到着', cf.arrived_num)
        if cf.arrived_num >= len(cf.clients):
            cf.is_stop_control = True
