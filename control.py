# 交差点で制御するプログラム

import json
import socket
from concurrent.futures import ThreadPoolExecutor

IPADDR: str = "127.0.0.1"
PORT: int = 65530

sock_sv: socket.socket = socket.socket(socket.AF_INET)
sock_sv.bind((IPADDR, PORT))
sock_sv.listen()

# データ受信関数
def recv_client(sock: socket.socket) -> None:
    while True:
        try:
            data_encode: bytes = sock.recv(1024)
            # 受信データ0バイト時は接続終了
            if data_encode == b"":
                break

            data_decode: str = data_encode.decode('utf-8')
            data = json.loads(data_decode)
            print(data)

        # 切断時の例外を捕捉したら終了
        except ConnectionResetError:
            break
    
    # クライアントをクローズ処理
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


print('⚡ control.py start')
while True:
    # クライアントの接続受付
    sock_cl, addr = sock_sv.accept()

    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(recv_client, sock_cl)