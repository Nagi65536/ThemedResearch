import sqlite3


conn = sqlite3.connect('./db/main.db', isolation_level=None)
cur = conn.cursor()


def main():
    create_table()
    register()


def register():
    data = []

    direction = ['n', 'e', 's', 'w']
    status = ['connect', 'stop', 'passed']

    for i in range(10):
        i_str = str(i)
        for s in status:
            for n, d in enumerate(direction):
                tag_id = f'tag_{d}_{s}_{i_str.zfill(3)}_id'
                tag_name = f'tag_{d}_{s}_{i_str.zfill(3)}'
                cross_name = f'cross_{i_str.zfill(3)}'
                cur.execute(f'INSERT INTO tag_info VALUES("{tag_id}", "{tag_name}", "{cross_name}", "{s}", "{n}")')


def create_table():
    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS tag_info(
        tag_id     TEXT PRIMARY KEY,
        tag_name   TEXT,
        cross_name TEXT,
        status     TEXT,
        direction  INTEGER
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS control(
        car_id      TEXT PRIMARY KEY,
        cross_name  TEXT,
        tag_id      TEXT,
        origin      INTEGER,
        destination INTEGER,
        status      TEXT, 
        time        INTEGER
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


if __name__ == '__main__':
    main()