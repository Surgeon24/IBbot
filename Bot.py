import threading
import time
from IBApi import IBApi
from Strategies import StrategyAdapter

class Bot:
    def __init__(self, server, strategy, symbol):
        self.strat = StrategyAdapter()
        self.strategy = strategy
        self.symbol = symbol
        self.isRunning = True
        self.server = server

    def start(self):
        self.thread = threading.Thread(target=self.createContractAndRunLoop, args=(self.symbol, self.strategy))
        self.thread.start()

    def createContractAndRunLoop(self, symbol, strategy):
        self.symbol = symbol
        self.contract = self.server.ib.createContract(self.symbol)
        self.strategyId = strategy

        while not isinstance(self.server.ib.nextOrderId, int):
            print('waiting for connection')
            time.sleep(1)

        print('connected')
        self.runStrategyLoop()

    def runStrategyLoop(self):
        if self.strategyId is None:
            print("Trading strategy not set properly.")
            return

        while self.isRunning:
            self.requestMarketData()
            action = self.strat.runStrategy(self.strategyId, self.server.ib.price_history)
            if action == "BUY":
                self.sendOrder("BUY")
            elif action == "SELL":
                self.sendOrder("SELL")
            elif action == "HOLD":
                print("No order placed.")
            else:
                print("Unresolved action:", action)
            time.sleep(5)

    def requestMarketData(self):
        # print("Market data request")
        self.server.ib.reqMktData(0, self.contract, "", False, False, [])
        self.server.ib.marketDataRequested = True

    def sendOrder(self, action):
        print(f"Placing {action} order for {self.symbol}")
        order = self.server.ib.sendOrder(self.contract, action)
        if order:
            self.server.ib.nextOrderId += 1
            # print("Order placed. Next order id will be", server.ib.nextOrderId)
        else:
            print("Failed to place the order.")

    # def run(self):
    #     while self.is_running:
    #         pass

    def stop(self):
        self.isRunning = False