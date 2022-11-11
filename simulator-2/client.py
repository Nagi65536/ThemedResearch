import time

import config as cf
from config import comms
from astar import a_star


def communicate(car_id, start_node, goal_node, delay=-1):
    print(f'{car_id}: 探索 {start_node} -> {goal_node}')

    while True:
        data = a_star(start_node, goal_node)
        if data and len(data) < 3:
            break
        congestion = congestion_check(car_id, data)
        if not congestion:
            break

    comms.add_client_data(car_id, data)

    if data and len(data) >= 3:
        comms.add_connect(car_id)
    else:
        print(f'{car_id}: 目的地到着')
        cf.arrived_num += 1
        if cf.arrived_num >= len(obj)(cf.clients):
            cf.is_stop_control = True


def congestion_check(car_id, data):
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    congestion = False
    cross_delay = 0

    for node in data:
        arrival_time = time.time() + node[1]/cf.CAR_SPEED + cross_delay
        cur.execute(f'''
        INSERT INTO cross_schedule VALUES (
            "{car_id}", "{node[0]}", "{arrival_time}"
        )''')

        cur.execute(f'''
        SELECT * FROM cross_schedule WHERE 
        cross="{node[0]}" AND
        time BETWEEN 
        {arrival_time + CHECK_CONGESTION_RANGE[0]} 
        {arrival_time + {arrival_time + CHECK_CONGESTION_RANGE[0]}}
        ''')
        cross_situation = cur.fetchall()

        for my_data in check_list:
            congestion = decide_can_entry(car_id, cross_situation)

            if congestion:
                break


def decide_can_entry(my_data, entry_list):
    for my_data in check_list:
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


def cross_process(car_id, front_cars=0):
    time.sleep(front_cars * cf.ENTRY_DELAY)

    # 交差点進入
    comms.add_entry(car_id)
    time.sleep(cf.CAR_PASSED_TIME)

    # 交差点通過
    comms.add_passed(car_id)
    dist = comms.get_next_cross_data(car_id)[1]
    wait_time = dist / cf.CAR_SPEED
    print(f'{car_id}: 移動 {wait_time:3.3}')
    time.sleep(wait_time)

    if len(comms.get_client_data(car_id)) >= 3:
        comms.add_connect(car_id)
    else:
        print(f'{car_id}: 目的地到着')
        cf.arrived_num += 1
        if cf.arrived_num >= len(cf.clients):
            cf.is_stop_control = True
