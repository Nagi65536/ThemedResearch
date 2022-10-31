# 自動車側の仮のプログラム

import json
import random
import socket
import sys
from time import sleep

IPADDR: str = "127.0.0.1"
PORT: int = 0

with open('./memo/port_share.txt', 'r') as f:
    PORT = int(f.read())

sock = socket.socket(socket.AF_INET)
sock.connect((IPADDR, PORT))
args = sys.argv


def get_encode_to_send(status, car_id, tag_id, destination) -> bytes:
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

    car_num = str(random.randint(1, 10000)).zfill(5)
    car_id = 'car_' + str(car_num)

    # 接続報告-送信
    send_data: bytes = get_encode_to_send(
        'connect', car_id, tag_id, destination)
    sock.send(send_data)

    # 指示-受信
    get_data: dict = get_decode_data(sock.recv(1024))
    print(f'{car_id} > {get_data["operate"]}')

    if get_data['operate'] == 'stop':
        # 進入指示-受信
        get_data = get_decode_data(sock.recv(1024))
        print(f'{car_id} > {get_data["operate"]}')

    if delay < 0:
        input('Please push ENTER to send "passed".')
    else:
        print(f'{car_id} 通過中')
        sleep(delay)

    # 通過済報告-送信
    send_data: bytes = get_encode_to_send(
        'passed', car_id, 'tag_s_connect_000_id', destination)
    sock.send(send_data)

    print(f'{car_id} 通過')

    return True


def main() -> None:
    if len(args) < 3:
        communication('r', 5)
    elif len(args) < 4:
        communication(args[1], int(args[2]))
    else:
        communication(args[1], int(args[2]), int(args[3]))


if __name__ == '__main__':
    print('⚡ client.py start')
    main()
