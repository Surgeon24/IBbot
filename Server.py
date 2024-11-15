import json
import asyncio
import websockets
import threading
from Bot import Bot
from BotAsync import BotAsync
from Test import Test

HOST = '192.168.31.250'
PORT = 8888

threads = {}

async def send_data(websocket):
    while True:
        # Пример данных для отправки на клиент
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
        await websocket.send(jsonString)
        await asyncio.sleep(10)

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

                    bot_instance = Bot()
                    # bot_instance = BotAsync()
                    # bot_instance = Test()
                    newThread = threading.Thread(target=bot_instance.createContractAndRunLoop, args=(symbol, strategy, threadId))
                    print(newThread)
                    newThread.start()
                    threads[threadId] = bot_instance
                    
                case "askAccountData":
                    await send_data(websocket)
                    
                case "stopStrategy":
                    threadId = arguments[0]
                    if threadId in threads:
                        print("\n\nFound thread to delete: ", threadId)
                        threadToStop = threads[threadId]
                        threadToStop.stop()
                        print(threadToStop)
                        del threads[threadId]

                case "stopAllStrategies":
                    for threadId, thread in threads.items():
                        threadToStop = threads[threadId]
                        threadToStop.stop()
                        del threads[threadId]

                case _:
                    print("Unhandled method:", method)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

async def main():
    async with websockets.serve(handle_client, HOST, PORT):
        print(f"WebSocket server started on ws://{HOST}:{PORT}")
        await asyncio.Future()  # Keeps the server running

# Запуск WebSocket сервера
asyncio.run(main())
