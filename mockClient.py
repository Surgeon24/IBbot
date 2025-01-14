import asyncio
import websockets
import json

HOST = '192.168.31.250'
PORT = '8888'

async def send_messages(websocket):
    """Отправка сообщений на сервер."""

    m = {
        "method": "askAccountData",
        "arguments": []
    }
    await websocket.send(json.dumps(m))
    print(f"Sent: {m}")
    
    await asyncio.sleep(2)

    m = {
        "method": "startStrategy",
        "arguments": ["AAPL", "1", "8801"]
    }
    await websocket.send(json.dumps(m))
    print(f"Sent: {m}")

    await asyncio.sleep(190)

    # m = {
    #     "method": "startStrategy",
    #     "arguments": ["AAPL", "2", "8802"]
    # }
    # await websocket.send(json.dumps(m))
    # print(f"Sent: {m}")

    # await asyncio.sleep(3)

    # m = {
    #     "method": "botList",
    #     "arguments": []
    # }
    # await websocket.send(json.dumps(m))
    # print(f"Sent: {m}")

    # await asyncio.sleep(5)

    m = {
        "method": "stopStrategy",
        "arguments": ["8801"]
    }
    await websocket.send(json.dumps(m))
    print(f"Sent: {m}")

    # await asyncio.sleep(3)

    # m = {
    #     "method": "stopStrategy",
    #     "arguments": ["8802"]
    # }
    # await websocket.send(json.dumps(m))
    # print(f"Sent: {m}")

async def receive_messages(websocket):
    """Получение сообщений от сервера."""
    try:
        async for message in websocket:
            print(f"Received: {message}")
    except websockets.ConnectionClosed:
        print("Connection closed by server")

async def test_client():
    uri = f"ws://{HOST}:{PORT}"  # Замените на актуальный адрес вашего сервера
    print("starting test_client")
    async with websockets.connect(uri) as websocket:
        # Запуск отправки и приёма сообщений параллельно
        send_task = asyncio.create_task(send_messages(websocket))
        receive_task = asyncio.create_task(receive_messages(websocket))

        # Дожидаемся завершения задач
        await asyncio.gather(send_task, receive_task)

# Запуск тестового клиента
print("starting")
# asyncio.run(test_client())
uri = f"ws://{HOST}:{PORT}"
send_messages(uri)

