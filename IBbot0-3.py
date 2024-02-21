import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.order import *

from ibapi.contract import Contract
import threading
import time

import socket
import threading

"""
Класс обработчик событий (wrapper). 
Он определяет методы для обработки событий:
подключение / оключение от сервера (connect / disconnect), обработка ошибок (error) и обновление цен (tickPrice).
"""
class IBApi(EWrapper, EClient):
    def __init__(self, bot):
        EClient.__init__(self, self)
        self.is_connected = False
        self.bot = bot
        self.price_history = []

    def connect(self, host, port, clientId):
        super().connect(host, port, clientId)
        self.is_connected = True

    def disconnect(self):
        super().disconnect()
        self.is_connected = False

    def error(self, id, errorCode, errorMsg):
        print(errorCode)
        print(errorMsg)

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        if tickType == 4:  # 4 corresponds to "Last Price" tick type
            self.bot.onPriceUpdate(price)
            self.price_history.append(price)


"""
Класс - торговый бот. В методе __init__() инициализируется объект IBApi, 
устанавливается соединение с сервером IB и запускается метод runLoop(). 
Затем определяются методы для запроса рыночных данных (requestMarketData), обработки обновлений цен (onPriceUpdate), 
размещения ордеров (placeOrder) и запуска основного цикла программы (runLoop).
"""
class Bot:
    ib = None
    marketDataRequested = False
    position = 0  # Initial position is flat
    tickerId = 0
    symbol = ""
    isRunning = False

    def __init__(self):
        self.ib = IBApi(self)
        ibThread = threading.Thread(target=self.runLoop, daemon=True)
        self.isRunning = True
        ibThread.start()
        time.sleep(1)

        # Create IB contract object
        print("Bot have been created. Create the contract you want to trade.")
        self.symbol = input("Enter the symbol you want to trade: ")
        self.contract = Contract()
        self.contract.symbol = self.symbol.upper()
        self.contract.secType = "STK"
        self.contract.exchange = "SMART"
        self.contract.currency = "USD"
        self.strategy = input("Enter id of strategy you want to trade (only 1 is avaliable rn):")

        print("Contract was created.")
        # Switch market data type to delayed (Type 3)
        self.ib.reqMarketDataType(3)
        # Request Market Data
        # self.requestMarketData()

        self.runStrategyLoop()

        # Ожидание завершения работы ibThread
        self.isRunning = False
        ibThread.join()

    def requestMarketData(self):
        if not self.marketDataRequested:
            print("Market data reqest. ticker id = ", self.tickerId)
            self.ib.reqMktData(self.tickerId, self.contract, "", False, False, [])
            self.marketDataRequested = True
            self.tickerId += 1
            if self.tickerId >= 10_000_000:
                self.tickerId = 0

    def onPriceUpdate(self, price):
        print("Current Price:", price)

    def placeOrder(self, action):
        print(f"Placing {action} order for {self.symbol}")
        
        #Create order object
        order = Order()
        order.action = action
        order.totalQuantity = 100
        order.orderType = 'MKT'


        #Place order
        self.ib.placeOrder(self.tickerId, self.contract, order)
        self.tickerId +=1

    def runLoop(self):
        self.ib.connect("127.0.0.1", 7497, 1)
        while self.isRunning:
            self.ib.run()
        self.ib.disconnect()

    def runStrategyLoop(self):
        # Проверяем, что стратегия установлена
        if self.strategy is None:
            print("Trading strategy doesn't set properly.")
            return

        while True:
            # Получаем текущую цену бумаги
            self.requestMarketData()
            current_price = self.ib.price_history

            #при добавлении новых стратегий здесь должен быть реализован переключатель
            #На данном этапе у нас есть только одна стратегия, которую мы и применяем
            action = self.strategy1(self.ib.price_history)
            # Выполняем действие в соответствии с решением стратегии
            if action == "BUY":
                self.placeOrder("BUY")
            elif action == "SELL":
                self.placeOrder("SELL")
            elif action == "HOLD":
                print("action HOLD was received. No order was placed.")
            else:
                print("unresolved action!")

            time.sleep(2)

    def strategy1(self, price_history):
        """
        Простая торговая стратегия на основе ценовой истории.
        Аргументы:
        - price_history: список последних цен закрытия, где цены упорядочены по возрастанию времени.
        Возвращает:
        - action: действие, которое необходимо выполнить (BUY - покупка, SELL - продажа, HOLD - держать позицию).
        """
        # Проверяем, что у нас есть достаточно данных для анализа
        if len(price_history) < 4:
            print("length of history price = ", len(price_history))
            return "HOLD"  # Если данных недостаточно, держим позицию
        # Получаем последние три цены закрытия
        last_three_prices = price_history[-3:]
        # Проверяем условие для покупки
        if all(last_three_prices[i] < last_three_prices[i + 1] for i in range(2)):
            return "BUY"
        # Проверяем условие для продажи
        if all(last_three_prices[i] > last_three_prices[i + 1] for i in range(2)):
            return "SELL"
        return "HOLD"

"""
Класс - торговый бот с сокет соединением, расширяющий класс Bot.
"""
class SocketBot(Bot):
    def __init__(self):
        self.symbol = None
        self.strategy = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', 12345))  #привязка к адресу и порту
        self.server_socket.listen(1)  #прослушивание входящих соединений

        #отдельный поток для принятия данных по сокету
        socket_thread = threading.Thread(target=self.accept_connections)
        socket_thread.start()

        super().__init__()

    def accept_connections(self):
        print("SocketBot is waiting for connections...")
        client_socket, _ = self.server_socket.accept()  # прием соединения
        print("SocketBot connected!")

        while True:
            data = client_socket.recv(1024).decode()  #данные от клиента
            if not data:
                break
            symbol, strategy = data.split(',')  #парсинг данных
            self.symbol = symbol
            self.strategy = strategy
            print(f"Received symbol: {symbol}, strategy: {strategy}")

        client_socket.close()

    def runLoop(self):
        # Изменяем метод runLoop() так, чтобы он использовал symbol и strategy из сокета
        if self.symbol is None or self.strategy is None:
            print("Symbol or strategy not set properly.")
            return

        self.contract.symbol = self.symbol.upper()
        self.strategy = self.strategy
        # Другие операции по инициализации

        # Далее продолжаем работу как обычно
        super().runLoop()

# Start the SocketBot
socket_bot = SocketBot()

# Start the Bot 
# bot = Bot()
