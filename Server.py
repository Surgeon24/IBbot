import ibapi
from Bot import Bot

import asyncio
import websockets
import sys
import json
from rx.subject import Subject
import threading
import time
from IBApi import IBApi
from Strategies import StrategyAdapter

class TradingServer:
    def __init__(self):
        print("init")
        self.ib = IBApi(self)
        self.ib.reqMarketDataType(3)
        self.isRunning = True
        self.active_bots = {}
        self.message_subject = Subject()

    def startBot(self, strategy_id, stock_id):
        if (strategy_id, stock_id) not in self.active_bots:
            bot = Bot(server, strategy_id, stock_id)
            bot.start()
            self.active_bots[(strategy_id, stock_id)] = bot
    
    def stopBot(self, strategy_id, stock_id):
        if (strategy_id, stock_id) in self.active_bots:
            bot = self.active_bots[(strategy_id, stock_id)]
            bot.stop()
            print(f"bot with strategy {strategy_id} and stock {stock_id} was stopped")
            del self.active_bots[(strategy_id, stock_id)]

    async def handle_message(self, websocket, path):
        async for message in websocket:
            self.message_subject.on_next(json.loads(message))

    def start_server(self, host, port):
        print("start IB connection")
        self.ibThread = threading.Thread(target=self.runLoop, daemon=True)
        self.ibThread.start()
        print("start the server")
        start_server = websockets.serve(self.handle_message, host, port)
        asyncio.get_event_loop().run_until_complete(start_server)

        # Subscribe to messages and react accordingly
        self.message_subject.subscribe(self.handle_bot_commands)

        asyncio.get_event_loop().run_forever()

    def handle_bot_commands(self, message):
        if message['method'] == 'startBot':
            self.startBot(message['strategy_id'], message['stock_id'])
        elif message['method'] == 'stopBot':
            self.stopBot(message['strategy_id'], message['stock_id'])

    def runLoop(self):
        self.ib.connect("127.0.0.1", 7497, 1)
        while self.isRunning:
            self.ib.run()
        self.ib.disconnect()

server = TradingServer()
HOST = '192.168.56.1'  # my localhost
PORT = 8888
server.start_server(HOST, PORT)