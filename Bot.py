import time
from IBApi import IBApi
from Strategies import StrategyAdapter

class Bot:
    ib = None
    strat = None
    marketDataRequested = False
    tickerId = 0
    symbol = ""
    params = {}
    isRunning = False
    timeChart = 5

    def __init__(self, ib, params):
        # self.ib = IBApi(self)
        self.strat = StrategyAdapter()
        self.isRunning = True
        self.ib = ib
        self.params = params
        self.updateTime(params)
        
        while self.isRunning:
            if isinstance(ib.nextOrderId, int):
                break
            else:
                print('waiting for connection (there is no nextOrderId)')
                time.sleep(2)

    def updateTime(self, params):
        print("updateTime")
        for key, value in params.items():
            if hasattr(self, key):
                print("found: ", key, " with value: ", value)
                setattr(self, key, value)

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

    def runStrategyLoop(self):
        if self.strategyId is None:
            print("Trading strategy doesn't set properly.")
            return
        while self.isRunning:
            self.tickerId += 1
            if self.tickerId > 99999:
                self.tickerId = 1
            self.requestMarketData()
            print("Ticker id:", self.tickerId)
            print("Next order id:", self.ib.nextOrderId)
            current_price = self.ib.price_history
            print("list of the last prices: ", current_price)

            
            action = self.strat.runStrategy(self.strategyId, self.ib.price_history, self.params)
            if action == "BUY":
                self.sendOrder("BUY")
            elif action == "SELL":
                self.sendOrder("SELL")
            elif action == "HOLD":
                print("action HOLD was received. No order was placed.")
            else:
                print("unresolved action:", action)
            if self.isRunning:
                time.sleep(self.timeChart)
    

    def getAccountData(self):
        print("getAccountData placeholder")
        info = self.ib.accountSummary(9001, "All", "$LEDGER", "StockValue", "USD")
        print(info)

    def stop(self):
        self.isRunning = False  # Останавливаем поток
