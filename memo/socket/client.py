import socket
import json

target_ip: str = "127.0.0.1"
target_port: int = 7776
buffer_size: int = 4096
id: int = 115291

# 1.ソケットオブジェクトの作成
tcp_client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2.サーバに接続
tcp_client.connect((target_ip,target_port))

send_data: list[str | int] = [str(id)]

while True:
    # 3.サーバにデータを送信
    send_data.append(input('> '))
    send_data_encode = json.dumps(send_data).encode()
    tcp_client.send(send_data_encode)

    # 4.サーバからのレスポンスを受信
    response = tcp_client.recv(buffer_size)
    print(f' < {response.decode("utf-8")}')
