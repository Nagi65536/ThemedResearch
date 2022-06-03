import socket

target_ip = "192.168.11.7"
target_port = 7777
buffer_size = 4096

# 1.ソケットオブジェクトの作成
tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2.サーバに接続
tcp_client.connect((target_ip,target_port))

data = None
while data != 'fin':
    # 3.サーバにデータを送信
    data = input('> ')
    tcp_client.send(data.encode())

    # 4.サーバからのレスポンスを受信
    response = tcp_client.recv(buffer_size)
    print(f' < {response.decode()}')