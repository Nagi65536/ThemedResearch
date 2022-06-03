import socket

server_ip = "192.168.11.7"
server_port = 7777
listen_num = 5
buffer_size = 1024

# 1.ソケットオブジェクトの作成
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2.作成したソケットオブジェクトにIPアドレスとポートを紐づける
tcp_server.bind((server_ip, server_port))

# 3.作成したオブジェクトを接続可能状態にする
tcp_server.listen(listen_num)

# 4.ループして接続を待ち続ける
while True:
    # 5.クライアントと接続する
    client,address = tcp_server.accept()
    print("- Connected! [{}]".format(address))

    data = None
    while data != 'fin':

        # 6.データを受信する
        data = client.recv(buffer_size)
        print(f' < {data.decode()}')

        # 7.クライアントへデータを返す
        # data = input('> ')
        data = 'hi'
        client.send(data.encode())

    # 8.接続を終了させる
    client.close()