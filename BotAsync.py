import asyncio
import threading
from IBApi import IBApi
from Strategies import StrategyAdapter

class BotAsync:
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
        self.isRunning = True

        # Запускаем основной асинхронный метод в отдельной задаче
        asyncio.create_task(self._async_init())  # Запускаем инициализацию как асинхронную задачу

    async def _async_init(self):
        await asyncio.sleep(1)  # Асинхронная пауза
        print("_init_")
        while self.isRunning:
            if isinstance(self.ib.nextOrderId, int):
                print('connected')
                break
            else:
                print('waiting for connection (there is no nextOrderId)')
                await asyncio.sleep(2)

    def start_contract_loop(self, symbol, strategy, id):
        # Эта функция будет работать в отдельном потоке
        # Для асинхронного выполнения используем asyncio.run_coroutine_threadsafe
        loop = asyncio.get_event_loop()
        future = asyncio.run_coroutine_threadsafe(self.createContractAndRunLoop(symbol, strategy, id), loop)
        future.result()  # Ожидаем завершения выполнения

    async def createContractAndRunLoop(self, symbol, strategy, id):
        print(f"Bot {id} has been created. Creating the contract...")
        self.symbol = symbol
        self.contract = self.ib.createContract(self.symbol)
        self.strategyId = strategy
        print("Contract was created.")

        # Switch market data type to delayed (Type 3)
        self.ib.reqMarketDataType(3)

        # Запуск асинхронной стратегии
        await self.runStrategyLoop()
        print("end of runStrategyLoop")
        await asyncio.sleep(1)
        self.isRunning = False

    def requestMarketData(self):
        if not self.marketDataRequested:
            print("Market data request. ticker id = ", self.tickerId)
            self.ib.reqMktData(self.tickerId, self.contract, "", False, False, [])
            self.marketDataRequested = True

    def onPriceUpdate(self, price):
        print("Current Price:", price)

    def sendOrder(self, action):
        print(f"Placing {action} order for {self.symbol}")
        order = self.ib.sendOrder(self.contract, action)
        if order:
            self.ib.nextOrderId += 1
            print("Order was placed. Next order id will be ", self.ib.nextOrderId)
        else:
            print("Failed to place the order.\n")

    async def runLoop(self):
        self.ib.connect("127.0.0.1", 7497, 1)
        while self.isRunning:
            self.ib.run()
        self.ib.disconnect()
        print("end of runLoop")

    async def runStrategyLoop(self):
        if self.strategyId is None:
            print("Trading strategy isn't set properly.")
            return
        while self.isRunning:
            print("\n\nrunStrategyLoop cycle... is running = ", self.isRunning)
            self.requestMarketData()
            print("tickerId:", self.tickerId)
            print("nextOrderId:", self.ib.nextOrderId)

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
                await asyncio.sleep(3)
            if self.isRunning:
                await asyncio.sleep(3)

    async def getAccountData(self):
        print("getAccountData placeholder")
        info = self.ib.accountSummary(9001, "All", "$LEDGER", "StockValue", "USD")
        print(info)

    def stop(self):
        self.isRunning = False  # Останавливаем поток
