import sqlite3
import tkinter
import math

SIZE_RATIO = 1

class MyApp1(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.last_create_point_l = None
        self.last_create_point_r = None
        self.point_l = []
        self.point_r = []
        self.isNew_l = False
        self.isNew_r = False
        self.cross_num = 0

        self.canvas = tkinter.Canvas(root, bg="white", width=800, height=450)
        self.canvas.bind('<Button-1>', self.l_click_canvas)
        self.canvas.bind('<Button-3>', self.r_click_canvas)
        self.canvas.pack()

        cur.execute('DELETE FROM cross_position')

    def l_click_canvas(self, event):
        if self.point_l and self.point_r:
            print('draw line')
            self.canvas.create_line(
                self.point_l[0], self.point_l[1],
                self.point_r[0], self.point_r[1]
            )
            self.canvas.create_oval(self.point_l[0]-7, self.point_l[1]-7, self.point_l[0]+7, self.point_l[1]+7, fill="black")
            self.canvas.create_oval(self.point_r[0]-7, self.point_r[1]-7, self.point_r[0]+7, self.point_r[1]+7, fill="black")

            self.point_l = [p * SIZE_RATIO for p in self.point_l]
            self.point_r = [p * SIZE_RATIO for p in self.point_r]

            coross_name_l = ''
            if not self.isNew_l:
                coross_name_l = str(self.cross_num).zfill(3)
                cur.execute(f'''
                    INSERT INTO cross_position VALUES (
                    "cross_{str(self.cross_num).zfill(3)}", {self.point_l[0]}, {self.point_l[1]}
                )''')
                self.cross_num += 1
            else:
                coross_name_l = self.isNew_l

            coross_name_r = ''
            if not self.isNew_r:
                coross_name_r = str(self.cross_num).zfill(3)
                cur.execute(f'''
                    INSERT INTO cross_position VALUES (
                    "cross_{str(self.cross_num+1).zfill(3)}", {self.point_r[0]}, {self.point_l[1]}
                )''')
                self.cross_num += 1
            else:
                coross_name_r = self.isNew_r

            dist = math.sqrt((self.point_r[0] - self.point_r[0]) ** 2 + (self.point_l[1] - self.point_l[1]) ** 2)
            cur.execute(f'''
                INSERT INTO road_info VALUES (
                "cross_{coross_name_l}",
                "cross_{coross_name_r}",
                {dist},
                0
            )
            ''')

            self.point_l = None
            self.point_r = None
            return

        print(f"L clicked → ({event.x}, {event.y})")
        node_info = search_node(event.x, event.y)
        if self.last_create_point_l:
            self.canvas.delete(self.last_create_point_l)

        if (not node_info):
            print("ノード追加")
            self.isNew_l = ''
            self.point_l = (event.x, event.y)
            self.last_create_point_l = self.canvas.create_oval(
                event.x-5, event.y-5, event.x+5, event.y+5, fill="blue")

        else:
            self.isNew_l = node_info
            self.point_l = (node_info["x"], node_info["y"])
            self.last_create_point_l = self.canvas.create_oval(
                node_info["x"]-5, node_info["y"]-5, node_info["x"]+5, node_info["y"]+5, fill="blue")

    def r_click_canvas(self, event):
        print(f"R clicked → ({event.x}, {event.y})")
        node_info = search_node(event.x, event.y)

        if self.last_create_point_r:
            self.canvas.delete(self.last_create_point_r)

        if (not node_info):
            print("ノード追加")
            self.isNew_r = ''
            self.point_r = (event.x, event.y)
            self.last_create_point_r = self.canvas.create_oval(
                event.x-5, event.y-5, event.x+5, event.y+5, fill="yellow")

        else:
            print("ノード既存", node_info["x"], node_info["y"])
            self.isNew_r = node_info
            self.point_r = (node_info["x"], node_info["y"])
            self.canvas.create_oval(node_info["x"]-5, node_info["y"]-5, node_info["x"]+5, node_info["y"]+5, fill="yellow")

    
def search_node(x, y):
    print("検索座標", x, y)
    cur.execute(f'''
    SELECT * FROM cross_position
    WHERE x BETWEEN {x-15} AND {x+15}
    AND y BETWEEN {y-15} AND {y+15}
    ''')
    res = cur.fetchone()
    print("結果", res)

    if (not res):
        return False
    else:
        return {"name": res[0], "x": res[1], "y": res[2]}


def db_init():
    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS cross_tag_info(
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

    cur.execute(f'''
    CREATE TABLE IF NOT EXISTS road_tag_info(
        tag_id TEXT,
        cross_name_1 TEXT,
        cross_name_2 TEXT
    )''')

    cur.execute('DELETE FROM cross_tag_info')
    cur.execute('DELETE FROM cross_position')
    cur.execute('DELETE FROM road_info')
    cur.execute('DELETE FROM control')
    cur.execute('DELETE FROM road_tag_info')
        

if __name__ == "__main__":
    conn = sqlite3.connect('./db/tmp.db', isolation_level=None)
    cur = conn.cursor()
    db_init()

    root = tkinter.Tk()
    root.geometry("800x450")
    root.title("マップ生成")
    app = MyApp1(master=root)
    app.mainloop()
