from cmath import sqrt
import sqlite3


dbname = "./db/sub.db"    # TODO
conn = sqlite3.connect(dbname, isolation_level=None)
cur = conn.cursor()


def between(tag_id, isStart):
    cur.execute(
        f"SELECT cross_name_1,cross_name_2 FROM road_tag_info WHERE tag_id = '{tag_id}' ")
    between_cross = cur.fetchone()

    cross_name = ""
    if between_cross:
        if isStart:
            cross_name = between_cross[0]
        else:
            cross_name = between_cross[1]
    else:
        cross_name = tag_id
    return cross_name


def a_star(start: str, goal: str,  *disable_nodes: tuple):
    disable_nodes = [d for d in disable_nodes]
    now_node = start    # 探索中のノード
    node_info = {start: [0, 0]}  # 各ノードの実際の距離とコスト
    route_info = {start: [start]}  # あるノードまでの最短経路

    while True:
        cur.execute(
            f"SELECT * FROM road_info WHERE cross_name_2 = '{now_node}' AND oneway != 1")
        connect_node_info = [(c[0], c[2]) for c in cur.fetchall()]

        cur.execute(
            f"SELECT * FROM road_info WHERE cross_name_1 = '{now_node}' AND oneway != 2")
        connect_node_info += [(c[1], c[2]) for c in cur.fetchall()]
        # now_nodeから移動可能なタグをconnect_node_infoとして格納

        # 接続しているノードnode_info計算
        have_connect_node = False
        for cn in connect_node_info:
            if cn[0] in disable_nodes:
                continue

            # cost = 実際の距離 + ゴールとの直線距離
            print("hello")
            dist = node_info[now_node][0] + cn[1]
            print("hello2")
            cost = euclid(cn[0], goal) + dist
            have_connect_node = True

            if not cn[0] in node_info or node_info[cn[0]][1] > cost:
                node_info[cn[0]] = [None, None]
                node_info[cn[0]][0] = dist
                node_info[cn[0]][1] = cost

                route_info[cn[0]] = [r for r in route_info[now_node]]
                route_info[cn[0]].append(cn[0])

        if not have_connect_node:
            # 経路が見つからなかった場合
            return None

        disable_nodes.append(now_node)
        node_info.pop(now_node)
        route_info.pop(now_node)

        # 次の now_node の適任を探す
        min = float('inf')
        for key in node_info:
            if (node_info[key][1] < min) and (not key in disable_nodes):
                min = node_info[key][1]
                now_node = key

        if now_node == goal:
            # 経路が見つかった場合
            return route_info[goal]


def euclid(cross_name, goal_name):
    cur.execute(
        f"SELECT * FROM cross_position WHERE cross_name = '{cross_name}' OR cross_name = '{goal_name}'")
    node_info = cur.fetchall()

    if len(node_info) == 1:
        return 0

    dist_x = abs(node_info[0][1] - node_info[1][1]) ** 2
    dist_y = abs(node_info[0][2] - node_info[1][2]) ** 2
    dist = abs(sqrt(dist_x + dist_y))

    return round(dist, 2)


def main(start_tag, goal_tag, *disable_nodes: tuple):
    start_cross = between(start_tag, True)
    goal_cross = between(goal_tag, False)

    print(start_cross)
    print(goal_cross)
    if start_cross and goal_cross:
        return a_star(start_cross, goal_cross, *disable_nodes)
    else:
        return ["err"]


if __name__ == '__main__':
    disable = []
    route = main("cross_002", "cross_006", *disable)
    print(route)
