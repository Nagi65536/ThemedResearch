import socket
import time

def main():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(("", 11411))
  sock.listen(1)

  print("waiting for socket connection")
  (clientsocket, address) = sock.accept()
  print("Established a socket connection from %s on port %s" % (address))
  s = clientsocket
  s.settimeout(0.5)

  cnt = 0
  while True:
    try:
      send_data = ['a', 'b', 'c']
      s.send(send_data[cnt % 3])
      cnt +=1
      try:
        rcv_data = s.recv(1, socket.MSG_DONTWAIT)
        print(rcv_data)
      except socket.timeout as e:
        pass

      time.sleep(1)
    except:
      s.close()

if __name__ == '__main__':
  main()