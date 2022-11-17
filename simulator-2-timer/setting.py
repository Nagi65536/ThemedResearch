import os
import sqlite3
import sys
import random
from cmath import sqrt

import config as cf


size = 12


def main():
    db_init()
    register_crosses_info()
    connect_cross_info()


def register_crosses_info(db_path=None):
    if db_path:
        conn = sqlite3.connect(f'{db_path}', isolation_level=None)
    else:
        conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)

    cur = conn.cursor()
    cross_num = 1
    global size
    for x in range(1, size + 1):
        for y in range(1, size + 1):
            x_position = x * 100 + random.randint(-30, 30)
            y_position = y * 100 + random.randint(-30, 30)
            cur.execute(
                f'INSERT INTO cross_position VALUES("cross_{str(cross_num).zfill(3)}", {x_position}, {y_position})'
            )
            cross_num += 1


def connect_cross_info(db_path):
    if db_path:
        conn = sqlite3.connect(f'{db_path}', isolation_level=None)
    else:
        conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)

    cur = conn.cursor()
    global size
    cross_num = 0
    while (True):  # 東
        cross_num += 1
        if cross_num % size == 0:
            continue
        else:
            cur.execute(
                f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num).zfill(3)}'"
            )
            node_1 = cur.fetchone()
            cur.execute(
                f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num + 1).zfill(3)}'"
            )
            node_2 = cur.fetchone()
            if not node_2:
                break
            cur.execute(
                f"INSERT INTO road_info VALUES('{node_1[0]}', '{node_2[0]}', {euclid(node_1, node_2)}, 1, 0)"
            )

    cross_num = 0

    while (True):  # 南
        cross_num += 1
        cur.execute(
            f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num).zfill(3)}'"
        )
        node_1 = cur.fetchone()
        cur.execute(
            f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num + size).zfill(3)}'"
        )
        node_2 = cur.fetchone()
        if not node_2:
            break
        cur.execute(
            f"INSERT INTO road_info VALUES('{node_1[0]}', '{node_2[0]}', {euclid(node_1, node_2)}, 2, 0)"
        )

    cross_num = 0
    while (True):  # 西
        cross_num += 1
        if cross_num % size == 1:
            continue
        else:
            cur.execute(
                f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num).zfill(3)}'"
            )
            node_1 = cur.fetchone()
            cur.execute(
                f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num - 1).zfill(3)}'"
            )
            node_2 = cur.fetchone()
            if not node_1:
                break
            cur.execute(
                f"INSERT INTO road_info VALUES('{node_1[0]}', '{node_2[0]}', {euclid(node_1, node_2)}, 3, 0)"
            )

    cross_num = 0
    while (True):  # 北
        cross_num += 1
        if cross_num <= size:
            continue
        else:
            cur.execute(
                f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num).zfill(3)}'"
            )
            node_1 = cur.fetchone()
            cur.execute(
                f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num - size).zfill(3)}'"
            )
            node_2 = cur.fetchone()
            if not node_1:
                break
            cur.execute(
                f"INSERT INTO road_info VALUES('{node_1[0]}', '{node_2[0]}', {euclid(node_1, node_2)}, 0, 0)"
            )


def db_init(db_path=None):
    if db_path:
        conn = sqlite3.connect(f'{db_path}', isolation_level=None)
    else:
        conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS control(
        car_id      TEXT,
        cross       TEXT,
        origin      INTEGER,
        destination INTEGER,
        status      TEXT, 
        time        REAL,
        pid         INTEGER
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS cross_schedule(
        car_id       TEXT,
        cross        TEXT,
        origin       INTEGER,
        destination  INTEGER,
        time         REAL,
        pid          INTEGER
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS cross_position(
        cross TEXT  PRIMARY KEY,
        x          REAL,
        y          REAL
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS road_info(
        cross_1 TEXT,
        cross_2 TEXT,
        dist         REAL,
        direction    INTEGER,
        oneway       INTEGER
    )''')

    cur.execute('DELETE FROM control')
    cur.execute('DELETE FROM cross_schedule')
    cur.execute('DELETE FROM cross_position')
    cur.execute('DELETE FROM road_info')


def euclid(node_1, node_2):
    dist_x = (node_1[1] - node_2[1])**2
    dist_y = (node_1[2] - node_2[2])**2
    return round(abs(sqrt(dist_x + dist_y)), 4)


def clear_db():
    conn = sqlite3.connect(cf.DB_PATH, isolation_level=None)
    cur = conn.cursor()
    cur.execute('DELETE FROM control')
    cur.execute('DELETE FROM cross_schedule')
    print('⚡️データベースを綺麗にしました')


def remove_db():
    if os.path.exists(cf.DB_PATH):
        os.remove(cf.DB_PATH)
        print('⚡️データベースを削除しました')
    else:
        print('⚡️データベースが見つかりませんでした')


def generate_db():
    print(f'⚡️GENERATE {cf.DB_PATH}')
    db_init(cf.DB_PATH)
    register_crosses_info(cf.DB_PATH)
    connect_cross_info(cf.DB_PATH)
    print('------------')
    print('')


if __name__ == '__main__':
    if 'clear' in sys.argv:
        clear_db()
    else:
        print('⚡️start setting.py')
        main()
