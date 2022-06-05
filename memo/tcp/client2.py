import socket

IPADDR = "127.0.0.1"
PORT = 7777

sock: socket.socket = socket.socket(socket.AF_INET)
sock.connect((IPADDR, PORT))

while True:
    # 任意の文字を入力
    data: str = input("> ")
    # exitを切断用コマンドとしておく
    if data == "exit":
        break
    else:
        try:
            sock.send(data.encode("utf-8"))
        except ConnectionResetError:
            break

# 送受信の切断
sock.shutdown(socket.SHUT_RDWR)
# ソケットクローズ
sock.close()