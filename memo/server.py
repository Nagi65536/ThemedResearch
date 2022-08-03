import socket
import struct
import time
import json
from contextlib2 import closing
UDP_IP="10.151.40.4"
UDP_PORT=9000

sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)
sock.bind((UDP_IP,UDP_PORT))

data = {"car_id":123456, "start":"tag_n_connect_000_id"}
data_json = json.dumps(data)

with closing(sock):
   while True:
       data,addr = sock.recvfrom(1024)
       time.sleep(1)
       #sock .sendto(b'hello\0',addr)
       mes = (data_json +'\0').encode()
       sock.sendto(mes,addr)