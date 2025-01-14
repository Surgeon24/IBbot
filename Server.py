import json
import asyncio
import websockets
import threading
from threading import Timer
from Bot import Bot
from IBApi import IBApi
from Data import Data

HOST = '192.168.31.250'
# HOST = '192.168.43.38'
PORT = 8888

ib = IBApi()
data = Data()
tickerId = 0
isRunning = True

threads = {}

async def handle_client(websocket, path):
    try:
        async for message in websocket:
            received_json = json.loads(message)
            method = received_json["method"]
            arguments = received_json["arguments"]

            print("Received JSON:")
            print("Method:", method)
            print("Arguments:", arguments)

            match method:
                case "startStrategy":
                    symbol = arguments[0]
                    strategy = arguments[1]
                    threadId = arguments[2]
                    params = arguments[3]

                    bot_instance = Bot(ib, params)
                    newThread = threading.Thread(target=bot_instance.createContractAndRunLoop, args=(symbol, strategy, threadId))
                    print(newThread)
                    newThread.start()
                    threads[threadId] = bot_instance
                    data.add_bot(threadId, symbol, strategy)


                case "botList":
                    print("\nbotList recieved!\n")
                    await data.send_bots_data(websocket)

                case "askAccountData":
                    await data.send_account_data(websocket, ib)
                    
                case "stopStrategy":
                    threadId = arguments[0]
                    if threadId in threads:
                        print("\n\nFound thread to delete: ", threadId)
                        threadToStop = threads[threadId]
                        threadToStop.stop()
                        print(threadToStop)
                        del threads[threadId]
                        data.remove_bot(threadId)

                case "stopAllStrategies":
                    for thread in threads.values():
                        thread.stop()
                    threads.clear()
                    data.remove_all_bots()


                case _:
                    print("Unhandled method:", method)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

def runLoop():
    ib.connect("127.0.0.1", 7497, 1)
    # ib.connect("127.0.0.1", 4002, 1)
    while isRunning:
        ib.run()
    ib.disconnect()

async def main():
    ibThread = threading.Thread(target=runLoop, daemon=True)
    ibThread.start()
    await asyncio.sleep(1)
    async with websockets.serve(handle_client, HOST, PORT):
        print(f"WebSocket server started on ws://{HOST}:{PORT}")
        await asyncio.Future()  # Keeps the server running

# Запуск WebSocket сервера
asyncio.run(main())
