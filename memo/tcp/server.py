import socket
import json

server_ip: str = "127.0.0.1"
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
    while not('fin' in decode_data):

        # 6.データを受信する
        data: bytes = client.recv(buffer_size)
        decode_data = json.loads(data.decode())

        print(f' < {decode_data}')

        # 7.クライアントへデータを返す
        send_data: str = 'ok'
        client.send(send_data.encode())

    # 8.接続を終了させる
    print('close')
    client.close()