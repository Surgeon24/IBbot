import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.order import *

from ibapi.contract import Contract
import threading
import time

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

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextOrderId = orderId
        print('The next valid order id is: ', self.nextOrderId)

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
        self.ib.nextOrderId = None
        ibThread = threading.Thread(target=self.runLoop, daemon=True)
        self.isRunning = True
        ibThread.start()
        time.sleep(1)

        while True:
            if isinstance(self.ib.nextOrderId, int):
                print('connected')
                break
            else:
                print('waiting for connection')
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
        order.totalQuantity = 10
        order.orderType = 'MKT'
        order.eTradeOnly = False
        order.firmQuoteOnly = False

        #Place order
        print("order id: ", self.ib.nextOrderId)
        self.ib.placeOrder(self.ib.nextOrderId, self.contract, order)
        self.ib.nextOrderId += 1
        print("order was placed. Next order id will be ", self.ib.nextOrderId)

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
            print("\n\nrunStrategyLoop cycle...")
            # Получаем текущую цену бумаги
            self.requestMarketData()
            print("tickerId:", self.tickerId)
            print("nextOrderId:", self.ib.nextOrderId)
            # current_price = self.ib.price_history

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

            time.sleep(3)


    """
    Простая торговая стратегия на основе ценовой истории.
    Аргументы:
    - price_history: список последних цен закрытия, где цены упорядочены по возрастанию времени.
    Возвращает:
    - action: действие, которое необходимо выполнить (BUY - покупка, SELL - продажа, HOLD - держать позицию).
    """
    def strategy1(self, price_history):

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

# Start the Bot 
bot = Bot()
