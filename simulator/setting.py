import sqlite3
import sys
import random


DB_NAME = sys.argv[1]
conn = sqlite3.connect(f'../db/{DB_NAME}', isolation_level=None)
cur = conn.cursor()


def main():
    db_init()
    register()


def register_crosses_info():
    cross_num = 1

    for x in range(7):
        for y in range(7):
            x_position = x * 100 + random.randint(-30, 30)
            y_position = y * 100 + random.randint(-30, 30)

    cur.execute(
        f'INSERT INTO cross_info VALUES("{tag_id}", "{tag_name}", "{cross_name}", "{s}", "{n}")')


def db_init():
    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS control(
        car_id      TEXT PRIMARY KEY,
        cross_now   TEXT,
        cross_from  TEXT,
        cross_to    TEXT,
        status      TEXT, 
        time        INTEGER
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS crosses_info(
        cross_name_1 TEXT,
        cross_name_2 TEXT,
        dist         REAL,
        oneway       INTEGER
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS cross_position(
        cross_name TEXT  PRIMARY KEY,
        x          REAL,
        y          REAL
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS road_info(
        cross_name_1 TEXT,
        cross_name_2 TEXT,
        dist         REAL,
        oneway       INTEGER
    )''')

    cur.execute('DELETE FROM control')
    cur.execute('DELETE FROM crosses_info')
    cur.execute('DELETE FROM cross_position')
    cur.execute('DELETE FROM road_info')


if __name__ == '__main__':
    main()
