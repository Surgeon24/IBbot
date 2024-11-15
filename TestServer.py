import asyncio
import websockets
import json
from threading import Thread, Event

HOST = '192.168.31.250'
PORT = 8888

class WorkerThread:
    def __init__(self):
        self.stop_event = Event()
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            print("Рабочий поток уже запущен.")
            return

        self.stop_event.clear()
        self.thread = Thread(target=self._run)
        self.thread.start()

    def _run(self):
        while not self.stop_event.is_set():
            print("Я работаю")
            self.stop_event.wait(1)

    def stop(self):
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join()
            print("Рабочий поток остановлен.")
        else:
            print("Рабочий поток не запущен.")

worker = WorkerThread()

async def handler(websocket):
    async for message in websocket:
        try:
            command = json.loads(message)
            if command.get("action") == "start":
                print("Получена команда 'старт'.")
                worker.start()
            elif command.get("action") == "stop":
                print("Получена команда 'стоп'.")
                worker.stop()
            else:
                print("Неизвестная команда:", command)
        except json.JSONDecodeError:
            print("Ошибка: Неверный формат JSON.")

async def main():
    async with websockets.serve(handler, HOST, PORT):
        print("Сервер запущен на ", HOST, PORT)
        await asyncio.Future()  # Бесконечное ожидание

if __name__ == "__main__":
    asyncio.run(main())
