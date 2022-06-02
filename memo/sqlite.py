import sqlite3

conn = sqlite3.connect('main.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS main(
    id INT PRIMARY KEY, 
    nodeFr TEXT, 
    nodeTo TEXT, 
    dist   FLOAT, 
    oneway INT)
    ''')

cur.execute('INSERT INTO main(id, nodeFr, nodeTo, dist, oneway) VALUES(1, "A", "B", 7, 0)')
res = cur.execute('SELECT * FROM main')
print(res)

conn.commit()