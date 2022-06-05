# 自動車側の仮のプログラム

import json
import socket
import random

IPADDR: str = "127.0.0.1"
PORT: int = 65530
CAR_ID = random.randint(10000, 99999)

sock: socket.socket = socket.socket(socket.AF_INET)
sock.connect((IPADDR, PORT))

print('⚡ tmp_client.py start')
while True:
    input('> ')
    data = {'carid': str(CAR_ID)}
    data_json: str = json.dumps(data)
    data_encode: bytes = data_json.encode('utf-8')

    try:
        sock.send(data_encode)
    except ConnectionResetError:
        break

# 送受信の切断
sock.shutdown(socket.SHUT_RDWR)
# ソケットクローズ
sock.close()
