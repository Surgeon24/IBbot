import threading
import time
from IBApi import IBApi
from Strategies import StrategyAdapter

class Bot:
    ib = None
    strat = None
    marketDataRequested = False
    position = 0  # Initial position is flat
    tickerId = 0
    symbol = ""
    isRunning = False

    def __init__(self):
        self.ib = IBApi(self)
        self.strat = StrategyAdapter()
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


    def createContractAndRunLoop(self, symbol, strategy):
        # Create IB contract object
        print("Bot have been created. Create the contract you want to trade.")
        self.symbol = symbol
        self.contract = self.ib.createContract(self.symbol)
        self.strategyId = strategy
        print("Contract was created.")

        # Switch market data type to delayed (Type 3)
        self.ib.reqMarketDataType(3)

        self.runStrategyLoop()

        # Ожидание завершения работы ibThread
        self.isRunning = False
        self.ibThread.join()

    def requestMarketData(self):
        if not self.marketDataRequested:
            print("Market data reqest. ticker id = ", self.tickerId)
            self.ib.reqMktData(self.tickerId, self.contract, "", False, False, [])
            self.marketDataRequested = True

    def onPriceUpdate(self, price):
        print("Current Price:", price)

    def sendOrder(self, action):
        print(f"Placing {action} order for {self.symbol}")
        order = self.ib.sendOrder(self.contract, action)
        if order:
            self.ib.nextOrderId += 1
            print("order was placed. Next order id will be ", self.ib.nextOrderId)
        else:
            print("failed to place the order.\n")

    def runLoop(self):
        self.ib.connect("127.0.0.1", 7497, 1)
        while self.isRunning:
            self.ib.run()
        self.ib.disconnect()

    def runStrategyLoop(self):
        # Проверяем, что стратегия установлена
        if self.strategyId is None:
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
            action = self.strat.runStrategy(self.strategyId, self.ib.price_history)
            if action == "BUY":
                self.sendOrder("BUY")
            elif action == "SELL":
                self.sendOrder("SELL")
            elif action == "HOLD":
                print("action HOLD was received. No order was placed.")
            else:
                print("unresolved action:", action)

            time.sleep(3)
