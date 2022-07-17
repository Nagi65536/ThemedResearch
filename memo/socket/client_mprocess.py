import socket
import json
import random
from typing import Any

IPADDR: str = "127.0.0.1"
PORT: int = 7777
CAR_ID: str = str(random.randint(10000, 99999))

sock: socket.socket = socket.socket(socket.AF_INET)
sock.connect((IPADDR, PORT))


def main() -> None:
    while True:
        # 任意の文字を入力
        data: str = input("> ")
        # exitを切断用コマンドとしておく
        condition: str = ""
        if data == "1":
            condition: str = "entry"
            print("entry")
        elif data == "2":
            print(stop)
            condition: str = "stop"
        elif data == "3":
            print("passing")
            condition: str = "passing"

        send_data: dict[str, Any] = {"carId": CAR_ID, "condition": condition}
        send_data_json = json.dumps(send_data)
        send_data_encode: bytes = send_data_json.encode("utf-8")

        result: int = socket_send(send_data_encode)

        if result:
            break

        if data == "1" or data == "2":
            data: str = socket_get()
            print(data)


def socket_send(send_data_encode: bytes) -> int:
    try:
        sock.send(send_data_encode)
        return 0
    except ConnectionResetError:
        # 送受信の切断
        sock.shutdown(socket.SHUT_RDWR)
        # ソケットクローズ
        sock.close()
        return 1

def socket_get():
    print('待機中')
    get_data: bytes = sock.recv(1024)
    data_json_decode: str = get_data.decode("utf-8")
    data: dict[str, Any] = json.loads(data_json_decode)
    print(data)
    
    return data

print('⚡ client_mprocess.py start')
if __name__ == "__main__":
    main()