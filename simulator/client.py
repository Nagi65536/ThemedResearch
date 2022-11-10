import time

import config as cf
from config import comms
from astar import a_star


def communicate(car_id, start_node, goal_node, delay=-1):
    print(f'{car_id}: 探索 {start_node} -> {goal_node}')
    data = a_star(start_node, goal_node)
    comms.add_client_data(car_id, data)

    if data and len(data) >= 3:
        comms.add_connect(car_id)
    else:
        print(f'{car_id}: 目的地到着')
        cf.arrived_num += 1
        if cf.arrived_num >= len(obj)(cf.clients):
            cf.is_stop_control = True


def cross_process(car_id):
    # 交差点進入
    comms.add_entry(car_id)
    time.sleep(cf.CAR_PASSED_TIME)

    # 交差点通過
    comms.add_passed(car_id)
    dist = comms.get_next_cross_data(car_id)[1]
    wait_time = dist / cf.CAR_SPEED
    print(f'{car_id}: 移動 {wait_time}')
    time.sleep(wait_time)

    if len(comms.get_client_data(car_id)) >= 3:
        comms.add_connect(car_id)
    else:
        print(f'{car_id}: 目的地到着')
        cf.arrived_num += 1
        if cf.arrived_num >= len(cf.clients):
            cf.is_stop_control = True
