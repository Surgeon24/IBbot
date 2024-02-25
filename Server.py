import ibapi
from Bot import Bot
import socket
import sys
import threading
import time
import json
 

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

print("starting the bot in the paralel thread")
bot = Bot()
isRunning = True
print('Socket is now waiting for the connection')
while True:
    conn, addr = s.accept()
    print('Connected with', addr)
    pair_json = conn.recv(64).decode()
    print('Received pair:', pair_json)
    # Extracting the string and integer from the received pair string
    symbol, value = json.loads(pair_json)
    
    if isRunning:
        bot.createContractAndRunLoop(symbol, value)
    
    
    conn.close()

s.close()

