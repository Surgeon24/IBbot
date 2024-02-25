import socket
import sys
 

HOST = '192.168.56.1'  # my localhost
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

try:
    s.bind((HOST, PORT))
except socket.error as err:
    print('Bind failed!, Error Code:', err)
    sys.exit()

print('Socket bind success!')
s.listen(10)
print('Socket is now listening')

while True:
    conn, addr = s.accept()
    print('Connected with ', addr)
    data = conn.recv(64).decode()
    print('Received:', data) 
    conn.close()

s.close()

