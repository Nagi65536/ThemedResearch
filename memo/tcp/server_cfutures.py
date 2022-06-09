import socket
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from numpy import byte

IPADDR: str = "127.0.0.1"
PORT: int = 7777

sock_sv: socket.socket = socket.socket(socket.AF_INET)
sock_sv.bind((IPADDR, PORT))
sock_sv.listen()

def main() -> None:
    while True:
        # クライアントの接続受付
        sock_cl, addr = sock_sv.accept()

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(recv_client, sock_cl, addr)


# データ受信ループ関数
def recv_client(sock: socket.socket, addr: tuple[str]) -> None:
    print(f"-connected {addr}")

    while True:
        try:
            data: str = socket_get(sock)
            car_id: str = data["carId"]
            condition: str = data["condition"]
            
            if condition == "entry":
                print("entry - go, stop")
                instruction = input("> ")

                send_data: dict[str, Any] = {"carId": car_id, "instruction": instruction}
                send_data_json = json.dumps(send_data)
                send_data_encode: bytes = send_data_json.encode("utf-8")

                result: int = socket_send(sock, send_data_encode)
                if result:
                    break

            elif condition == "stop":
                print("stop - go")
                input("> ")
                send_data: dict[str, Any] = {"carId": car_id, "instruction": "go"}
                send_data_json = json.dumps(send_data)
                send_data_encode: bytes = send_data_json.encode("utf-8")

                result: int = socket_send(sock, send_data_encode)
                if result:
                    break
            
            else:
                break

        except ConnectionResetError:
            break
    
    # クライアントをクローズ処理
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


def socket_send(sock: socket.socket, send_data_encode: bytes) -> int:
    try:
        print('ok')
        sock.send(send_data_encode)
        print('send')
        return 0

    except ConnectionResetError:
        # 送受信の切断
        sock.shutdown(socket.SHUT_RDWR)
        # ソケットクローズ
        sock.close()
        return 1


def socket_get(sock: socket.socket) -> dict[str, Any]:
    print("待機中")
    get_data: bytes = sock.recv(1024)
    data_json_decode: str = get_data.decode("utf-8")
    data: dict[str, Any] = json.loads(data_json_decode)
    
    return data
    

print('⚡ server_cfutures.py start')
if __name__ == "__main__":
    main()