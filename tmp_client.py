# 自動車側の仮のプログラム

import json
import socket
import random

IPADDR: str = "127.0.0.1"
PORT: int = 65530
CAR_ID = 'car_' + str(random.randint(10000, 99999))

sock = socket.socket(socket.AF_INET)
sock.connect((IPADDR, PORT))


def get_encode_to_send(status, tag_id, destination):
    data = {'car_id': str(CAR_ID), 'status': status, 'tag_id': tag_id, 'destination': destination}
    data_json: str = json.dumps(data)
    data_encode: bytes = data_json.encode('utf-8')

    return data_encode

communication
def get_decode_data(data):
    data_decode: str = data.decode('utf-8')
    data_py_obj = json.loads(data_decode)

    return data_py_obj



def communication():
    input('Please push ENTER to send "connect".')

    # 接続報告-送信
    send_data = get_encode_to_send('connect', 'tag_n_connect_000_id', 1)
    sock.send(send_data)

    # 指示-受信
    get_data = get_decode_data(sock.recv(1024))
    print(get_data)

    if get_data['operate'] == 'stop':
        # 進入指示-受信
        get_data = get_decode_data(sock.recv(1024))
        print(get_data)

    input('Please push ENTER to send "passed".')

    # 通過済報告-送信
    send_data = get_encode_to_send('passed', 'tag_s_connect_000_id', 1)
    sock.send(send_data)


def main():
    communication()


if __name__ == '__main__':
    print('⚡ tmp_client.py start')
    main()