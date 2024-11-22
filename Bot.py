import threading
import time
import _asyncio
from IBApi import IBApi
from Strategies import StrategyAdapter

class Bot:
    ib = None
    strat = None
    marketDataRequested = False
    tickerId = 0
    symbol = ""
    isRunning = False

    def __init__(self, ib):
        # self.ib = IBApi(self)
        self.strat = StrategyAdapter()
        self.isRunning = True
        self.ib = ib

        # ibThread = threading.Thread(target=self.runLoop, daemon=True)
        # ibThread.start()
        # time.sleep(1)
        
        print("_init_")
        while self.isRunning:
            if isinstance(ib.nextOrderId, int):
                break
            else:
                print('waiting for connection (there is no nextOrderId)')
                time.sleep(2)
        print("end of _init_")


    def createContractAndRunLoop(self, symbol, strategy, id):
        # Create IB contract object
        print(f"Bot {id} has been created. Creating the contract...")
        self.symbol = symbol
        self.contract = self.ib.createContract(self.symbol)
        self.strategyId = strategy
        print("Contract was created.")

        # Switch market data type to delayed (Type 3)
        self.ib.reqMarketDataType(3)
        self.runStrategyLoop()
        self.isRunning = False
        print("end of createContractAndRunLoop")
        

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

    # def runLoop(self):
    #     self.ib.connect("127.0.0.1", 7497, 1)
    #     while self.isRunning:
    #         self.ib.run()
    #     self.ib.disconnect()
    #     print("end of runLoop")

    def runStrategyLoop(self):
        # Проверяем, что стратегия установлена
        if self.strategyId is None:
            print("Trading strategy doesn't set properly.")
            return
        while self.isRunning:
            print("\n\nrunStrategyLoop cycle... is running = ", self.isRunning)
            # Получаем текущую цену бумаги
            self.requestMarketData()
            print("tickerId:", self.tickerId)
            print("nextOrderId:", self.ib.nextOrderId)
            current_price = self.ib.price_history
            print("current price: ", current_price)
            
            action = self.strat.runStrategy(self.strategyId, self.ib.price_history)
            if action == "BUY":
                self.sendOrder("BUY")
            elif action == "SELL":
                self.sendOrder("SELL")
            elif action == "HOLD":
                print("action HOLD was received. No order was placed.")
            else:
                print("unresolved action:", action)
            if self.isRunning:
                time.sleep(2)
    

    def getAccountData(self):
        print("getAccountData placeholder")
        info = self.ib.accountSummary(9001, "All", "$LEDGER", "StockValue", "USD")
        print(info)
        # self.ib.reqAccountSummary(9001, "All", "NetLiquidation,SMA,StockValue")

    def stop(self):
        self.isRunning = False  # Останавливаем поток
