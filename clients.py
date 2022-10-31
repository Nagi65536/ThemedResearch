# 自動車側の仮のプログラム

from concurrent.futures import ThreadPoolExecutor
import json
import random
import socket
import sys
import time


clients = [
    # (前の車との遅延, 来る方向, 行き先, 通過時間)
    (0, 0, 2, 3),
    (1, 0, 2, 3),
]
PROCESS_DELAY = 0.1


def get_encode_data(status, car_id, tag_id, destination) -> bytes:
    data: dict = {'car_id': str(car_id), 'status': status,
                  'tag_id': tag_id, 'destination': destination}
    data_json: str = json.dumps(data)
    data_encode: bytes = data_json.encode('utf-8')

    return data_encode


def get_decode_data(data) -> dict:
    data_decode: str = data.decode('utf-8')
    data_py_obj: dict = json.loads(data_decode)

    return data_py_obj


def communication(origin, destination, delay=-1) -> bool:
    if origin == 'r':
        dir_list = ['n', 'e', 's', 'w']
        tag_id = f'tag_{random.choice(dir_list)}_connect_000_id'
    else:
        dir_list = ['n', 'e', 's', 'w']
        i = (int(origin) + int(destination)) % 4
        tag_id = f'tag_{dir_list[i]}_connect_000_id'

    if destination > 4:
        destination = random.randint(0, 3)

    try:
        global car_num
        car_num += 1
        car_id = 'car_' + str(car_num).zfill(3)

        # 接続報告-送信
        send_data: bytes = get_encode_data(
            'connect', car_id, tag_id, destination)
        sock.send(send_data)
        print(f'{car_id} < connect')

        # 指示-受信
        get_data = None
        while not get_data:
            if car_id in recv_datum:
                get_data = recv_datum.pop(car_id)
            time.sleep(PROCESS_DELAY)

        print(f'{car_id} > {get_data["operate"]}')

        if get_data['operate'] == 'stop':
            # 進入指示-受信
            get_data = None
            while not get_data:
                if car_id in recv_datum:
                    get_data = recv_datum.pop(car_id)
                time.sleep(PROCESS_DELAY)
            print(f'{car_id} > {get_data["operate"]}')

        print(f'{car_id} 通過中')
        time.sleep(delay)

        # 通過済報告-送信
        send_data: bytes = get_encode_data(
            'passed', car_id, 'tag_s_passed_000_id', destination)
        sock.send(send_data)
        print(f'{car_id} < passed')

        return True
    except:
        return False


def distribute_recv_data():
    while True:
        get_data = get_decode_data(sock.recv(1024))
        recv_datum[get_data['car_id']] = get_data
        time.sleep(PROCESS_DELAY)


def main() -> None:
    with ThreadPoolExecutor() as executor:
        executor.submit(distribute_recv_data)
        start_time = time.time()

        with ThreadPoolExecutor() as executor:

            for i, client in enumerate(clients):
                executor.submit(communication, client[1], client[2], client[3])

                if len(clients) > i+1:
                    time.sleep(clients[i+1][0])

        print()
        print(f'経過時間 : {time.time() - start_time:.2f}s')



if __name__ == '__main__':
    IPADDR: str = "127.0.0.1"
    PORT: int = 0

    with open('./memo/port_share.txt', 'r') as f:
        PORT = int(f.read())

    sock = socket.socket(socket.AF_INET)
    sock.connect((IPADDR, PORT))
    
    car_num = 0
    recv_datum = {}

    print('⚡ clients.py start')
    main()
