from cmath import sqrt
import sqlite3

dbname = "../db/main.db"


def a_star(start: str, goal: str,  *disable_nodes: tuple):
    conn = sqlite3.connect(dbname, isolation_level=None)
    cur = conn.cursor()
    
    disable_nodes = [d for d in disable_nodes]
    now_node = start
    node_info = {start: [0, 0]}
    route_info = {start: [start]}

    while True:
        sql = f"SELECT * FROM road_info WHERE cross_name_2 = '{now_node}' AND oneway != 1"
        cur.execute(sql)
        can_move_node_tmp = cur.fetchall()
        connect_node_info = [(c[0], c[2]) for c in can_move_node_tmp]

        sql = f"SELECT * FROM road_info WHERE cross_name_1 = '{now_node}' AND oneway != 2"
        cur.execute(sql)
        can_move_node_tmp = cur.fetchall()
        connect_node_info += [(c[1], c[2]) for c in can_move_node_tmp]

        # 接続しているノードnode_info計算
        have_connect_node = False
        for cn in connect_node_info:
            # cn = ("cross_name", now_nodeとの距離)

            if cn[0] in disable_nodes:
                continue

            have_connect_node = True
            dist1 = node_info[now_node][0] + cn[1]
            dist2 = euclid(cn[0], goal)
            cost = dist1 + dist2

            if not cn[0] in node_info:
                node_info[cn[0]] = [0, 0]
                node_info[cn[0]][0] = dist1
                node_info[cn[0]][1] = cost

                route_info[cn[0]] = [r for r in route_info[now_node]]
                route_info[cn[0]].append(cn[0])

            elif node_info[cn[0]][1] > cost:
                node_info[cn[0]][0] = dist1
                node_info[cn[0]][1] = cost
                route_info[cn[0]] = [r for r in route_info[now_node]]
                route_info[cn[0]].append(cn[0])

        if not have_connect_node:
            return '404 NOT FOUND!'

        disable_nodes.append(now_node)

        # 次のnow_nodeの適任を探す
        min = float('inf')
        for key in node_info:
            if (node_info[key][1] < min) and (not key in disable_nodes):
                min = node_info[key][1]
                now_node = key

        if now_node == goal:
            return route_info[goal]


def euclid(cross_name, goal_name):
    node_info = []
    conn = sqlite3.connect(dbname, isolation_level=None)
    cur = conn.cursor()
    sql = f"SELECT * FROM cross_position WHERE cross_name = '{cross_name}' OR cross_name = '{goal_name}'"
    cur.execute(sql)
    node_info = cur.fetchall()

    if len(node_info) == 1:
        return 0

    dist_x = abs(node_info[0][1] - node_info[1][1])**2
    dist_y = abs(node_info[0][2] - node_info[1][2])**2
    dist = abs(sqrt(dist_x + dist_y))

    return round(dist, 2)


disable = ['cross_004', 'cross_003']
if __name__ == '__main__':
    root = a_star("cross_000", "cross_007", *disable)
    print(root)
