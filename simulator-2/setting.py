import sqlite3
import random
from cmath import sqrt

import config as cf


conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
cur = conn.cursor()


def main():
    db_init()
    register_crosses_info()
    connect_cross_info()


def register_crosses_info():
    cross_num = 1

    for x in range(1, 7):
        for y in range(1, 7):
            x_position = x * 100 + random.randint(-30, 30)
            y_position = y * 100 + random.randint(-30, 30)
            cur.execute(
                f'INSERT INTO cross_position VALUES("cross_{str(cross_num).zfill(3)}", {x_position}, {y_position})'
            )
            cross_num += 1


def connect_cross_info():
    cross_num = 0
    while (True):
        cross_num += 1
        if cross_num % 6 == 0:
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

    while (True):
        cross_num += 1
        cur.execute(
            f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num).zfill(3)}'"
        )
        node_1 = cur.fetchone()
        cur.execute(
            f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num + 6).zfill(3)}'"
        )
        node_2 = cur.fetchone()
        if not node_2:
            break
        cur.execute(
            f"INSERT INTO road_info VALUES('{node_1[0]}', '{node_2[0]}', {euclid(node_1, node_2)}, 2, 0)"
        )

    cross_num = 0
    while (True):
        cross_num += 1
        if cross_num % 6 == 1:
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
    while (True):
        cross_num += 1
        if cross_num <= 6:
            continue
        else:
            cur.execute(
                f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num).zfill(3)}'"
            )
            node_1 = cur.fetchone()
            cur.execute(
                f"SELECT * FROM cross_position WHERE cross = 'cross_{str(cross_num - 6).zfill(3)}'"
            )
            node_2 = cur.fetchone()
            if not node_1:
                break
            cur.execute(
                f"INSERT INTO road_info VALUES('{node_1[0]}', '{node_2[0]}', {euclid(node_1, node_2)}, 0, 0)"
            )


def db_init():
    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS control(
        car_id      TEXT PRIMARY KEY,
        cross  TEXT,
        origin      INTEGER,
        destination INTEGER,
        status      TEXT, 
        time        REAL
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS cross_schedule(
        car_id       TEXT,
        cross        TEXT,
        origin       INTEGER,
        destination  INTEGER,
        time         REAL
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


if __name__ == '__main__':
    print('⚡️start setting.py')
    main()
