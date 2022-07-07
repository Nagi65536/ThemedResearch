import sqlite3


conn = sqlite3.connect('./db/main.db', isolation_level=None)
cur = conn.cursor()


def main():
    create_table()


def register():
    data = []

    direction = ['n', 'e', 's', 'w']
    variable = ['connect_', 'stop_', 'passed_']

    data.append(input('交差点ID > '))
    for d in direction:
        for v in variable:
            data.append(f'{v}{d}')

    cur.execute(
        f'INSERT INTO cross_tag VALUES("{data[0]}", "{data[1]}", "{data[2]}", "{data[3]}", "{data[4]}", "{data[5]}", "{data[6]}", "{data[7]}", "{data[8]}", "{data[9]}", "{data[10]}", "{data[11]}", "{data[12]}")')


def create_table():
    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS tag_info(
        tag_id     TEXT PRIMARY KEY,
        tag_name   TEXT,
        cross_name TEXT
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS control(
        car_id      TEXT PRIMARY KEY,
        cross_name  TEXT,
        tag_id      TEXT,
        destination TEXT,
        status      TEXT, 
        time        TEXT
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS cross_position(
        cross_name TEXT  PRIMARY KEY,
        x          REAL,
        y          REAL
    )''')

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS road_connection(
    )''')


if __name__ == '__main__':
    main()
