import sqlite3
import random
from cmath import sqrt

import config as cf


conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
cur = conn.cursor()


def main():
    db_init()


def db_init():
    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS control(
        car_id      TEXT PRIMARY KEY,
        origin      INTEGER,
        destination INTEGER,
        status      TEXT, 
        time        REAL,
        pid         TEXT
    )''')

    cur.execute('DELETE FROM control')


if __name__ == '__main__':
    print('⚡️start setting.py')
    main()
