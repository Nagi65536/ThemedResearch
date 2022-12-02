import glob
import sys
import os
import sqlite3
import random
from cmath import sqrt

import config as cf


def main():
    print('⚡️start setting.py')
    db_init()


def db_init(table_name='control'):
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name}(
        car_id      TEXT,
        origin      INTEGER,
        destination INTEGER,
        status      TEXT, 
        time        REAL
    )''')

    cur.execute(f'DELETE FROM {table_name}')


def db_clear():
    files = glob.glob("./db/*")
    for file in files:
        os.remove(file)
    print('⚡️データベースフォルダーを綺麗にしました')


def remove_table(table_name='control'):
    conn = sqlite3.connect(f'{cf.DB_PATH}', isolation_level=None)
    cur = conn.cursor()
    cur.execute(f'DROP TABLE {table_name}')


def remove_db():
    files = glob.glob("./db/*")
    if cf.DB_NAME in files:
        os.remove(cf.DB_NAME)


def generate_db():
    print(f'⚡️GENERATE {cf.DB_PATH}')
    db_init()
    print('------------')
    print('')


if __name__ == '__main__':
    if 'clear' in sys.argv:
        db_clear()
    else:
        main()
