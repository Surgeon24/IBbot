import asyncio
import websockets
import json
import time
HOST = '192.168.31.250'
PORT = '8888'


async def test_client():
    uri = "ws://192.168.31.250:8888"  # Замените на актуальный адрес вашего сервера

    async with websockets.connect(uri) as websocket:
        # Отправляем первую команду "startStrategy"
        start_message_1 = {
            "method": "startStrategy",
            "arguments": ["AAPL", "1", "9902"]
        }
        await websocket.send(json.dumps(start_message_1))
        print(start_message_1)
        print("Sent startStrategy command for strategy 9902")

        await asyncio.sleep(5)

        # # Отправляем вторую команду "startStrategy"
        # start_message_2 = {
        #     "method": "startStrategy",
        #     "arguments": ["AAPL", "2", "9903"]
        # }
        # await websocket.send(json.dumps(start_message_2))
        # print("Sent startStrategy command for strategy 9903")

        # await asyncio.sleep(5)


        # # Отправляем команду "stopStrategy" для первой стратегии
        # stop_message_1 = {
        #     "method": "stopStrategy",
        #     "arguments": ["9903"]
        # }
        # await websocket.send(json.dumps(stop_message_1))
        # print("Sent stopStrategy command for strategy 9903")

        # await asyncio.sleep(10)

        # Отправляем команду "stopStrategy" для второй стратегии
        stop_message_2 = {
            "method": "stopStrategy",
            "arguments": ["9902"]
        }
        await websocket.send(json.dumps(stop_message_2))
        print("Sent stopStrategy command for strategy 9902")
        print(stop_message_2)



async def test_client_2():
    uri = "ws://192.168.31.250:8888"  # Замените на актуальный адрес вашего сервера

    async with websockets.connect(uri) as websocket:
        start_message = {"action": "start"}
        await websocket.send(json.dumps(start_message))
        print("Sent start")
        await asyncio.sleep(3)

        stop_message = {"action": "stop"}
        await websocket.send(json.dumps(stop_message))
        print("Sent stop")
        await asyncio.sleep(3)

        await websocket.send(json.dumps(stop_message))
        print("Sent stop again")
        await asyncio.sleep(3)

        await websocket.send(json.dumps(start_message))
        print("Sent start again")
        await asyncio.sleep(3)

        await websocket.send(json.dumps(stop_message))
        print("Sent stop again")
        await asyncio.sleep(3)




# Запуск тестового клиента
asyncio.run(test_client())

