# 自動車側の仮のプログラム

import json
import socket
import random

IPADDR: str = "127.0.0.1"
PORT: int = 65530
CAR_ID = random.randint(10000, 99999)

sock: socket.socket = socket.socket(socket.AF_INET)
sock.connect((IPADDR, PORT))


def main():
    print('⚡ tmp_client.py start')
    exchange()


def exchange():
    input('Please push ENTER. ')

    # 接続開始し、交差点エリア進入を報告
    data = get_json('connect', 'from')
    data = {'carid': str(CAR_ID), 'condition': 'connect', 'tagId': 'abc123'}
    data_json: str = json.dumps(data)
    data_encode: bytes = data_json.encode('utf-8')

    sock.send(data_encode)

    data_decode: str = 'stop'
    while data_decode == 'stop':
        data_encode: bytes = sock.recv(1024)
        data_decode: str = data_encode.decode('utf-8')
        print(data_decode)

    input('> ok?')
    data = {'carid': str(CAR_ID), 'condition': 'passed', 'tagId': 'def123'}
    data_json: str = json.dumps(data)
    data_encode: bytes = data_json.encode('utf-8')
    sock.send(data_encode)

    # 送受信の切断
    sock.shutdown(socket.SHUT_RDWR)
    # ソケットクローズ
    sock.close()


def get_json(condition, tag_id):
    return {'carid': str(CAR_ID), 'condition': condition, 'tagId': tag_id}


if __name__ == '__main__':
    main()