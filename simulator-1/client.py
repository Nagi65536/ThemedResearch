import time

import config as cf
from config import comms


def communicate(car_id, start, goal):
    comms.add_connect(car_id, start, goal)


def cross_process(car_id, front_cars=0):
    delay = front_cars * cf.ENTRY_DELAY

    # 交差点進入
    comms.add_entry(car_id, delay)
    time.sleep(cf.CAR_PASSED_TIME)

    # 交差点通過
    comms.add_passed(car_id)

    cf.arrived_num += 1
    if cf.arrived_num >= len(cf.clients):
        cf.is_stop_control = True
