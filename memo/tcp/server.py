import socket
import json

server_ip: str = "192.168.11.7"
server_port: int = 7776
listen_num: int = 5
buffer_size: int = 1024

# 1.ソケットオブジェクトの作成
tcp_server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2.作成したソケットオブジェクトにIPアドレスとポートを紐づける
tcp_server.bind((server_ip, server_port))

# 3.作成したオブジェクトを接続可能状態にする
tcp_server.listen(listen_num)

# 4.ループして接続を待ち続ける
while True:
    # 5.クライアントと接続する
    client, address = tcp_server.accept()
    print("- Connected! [{}]".format(address))

    decode_data: str = ''
    while decode_data != 'fin':

        # 6.データを受信する
        data: bytes = client.recv(buffer_size)
        decode_data = data.decode()

        for d in decode_data:
            print(f' < {d}')

        # 7.クライアントへデータを返す
        send_data: str = 'ok'
        client.send(send_data.encode())

    # 8.接続を終了させる
    client.close()