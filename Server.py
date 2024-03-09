import ibapi
from Bot import Bot
import socket
import sys
import threading
import time
import json


def sendData(s):
    while True:

        balance = 1000
        activeStrategies = 0
        acceptedStrategies = 0
        ownStrategies = 0

        accountData = {
            "balance": balance,
            "activeStrategies": activeStrategies,
            "acceptedStrategies": acceptedStrategies,
            "ownStrategies": ownStrategies
        }
        
        
        jsonString = json.dumps(accountData)

        # Send the JSON through the socket
        s.send(jsonString.encode())
        time.sleep(10) 

HOST = '192.168.56.1'  # my localhost
PORT = 8888
threads = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

try:
    s.bind((HOST, PORT))
except socket.error as err:
    print('Bind failed!, Error Code:', err)
    sys.exit()

print('Socket bind success!')
s.listen(10)

isRunning = True

connection, client_address = s.accept()
print('Connection from:', client_address)
print('Create second thread to send data')
data_thread = threading.Thread(target=sendData, args=(connection,))
# data_thread.start()

print('Socket is now waiting for the connection')
bot = Bot()
while True:
    conn, addr = s.accept()
    print('Connected with', addr)
    receivedData = conn.recv(1024).decode()
    print('Received data:', receivedData)
    # Deserialize the received JSON string back into a tuple
    received_json = json.loads(receivedData)
    method = received_json["method"]
    arguments = received_json["arguments"]

    print("Deserialize the received JSON:")
    print("First argument:", method)
    print("Second argument:", arguments)

    match method:
            case "startStrategy":
                symbol = arguments[0]
                strategy = arguments[1]
                threadId = arguments[2]
                newThread = threading.Thread(target=bot.createContractAndRunLoop, args=(symbol,strategy, threadId))
                newThread.start()
                threads[threadId] = newThread
            case "askAccountData":
                bot.getAccountData()
            case "stopStrategy":
                threadId = arguments[0]
                if threadId in threads:
                    print("\n\nfound thread to delete\n")
                    threadToStop = threads[threadId]
                    del threads[threadId]
                    threadToStop.join()
            case "stopAllStrategies":
                for threadId, thread in threads.items():
                    thread.join()
            case _:
                print("Unhandled method: ", method)
    
    conn.close()

