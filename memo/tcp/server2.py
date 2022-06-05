import socket
# スレッドライブラリ取り込み
import threading

IPADDR: str = "127.0.0.1"
PORT: int = 7776

sock_sv: socket.socket = socket.socket(socket.AF_INET)
sock_sv.bind((IPADDR, PORT))
sock_sv.listen()

# データ受信ループ関数
def recv_client(sock: socket.socket, addr: tuple[str]) -> None:
    while True:
        try:
            data = sock.recv(1024)
            # 受信データ0バイト時は接続終了
            if data == b"":
                break
            print(data.decode("utf-8"))
        # 切断時の例外を捕捉したら終了
        except ConnectionResetError:
            break
    
    # クライアントをクローズ処理
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


# クライアント接続ループ
while True:
    # クライアントの接続受付
    sock_cl, addr = sock_sv.accept()
    
    # スレッドクラスのインスタンス化
    thread = threading.Thread(target=recv_client, args=(sock_cl, addr))
    # スレッド処理開始
    thread.start()