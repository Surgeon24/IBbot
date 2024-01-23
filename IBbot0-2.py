# import talib
import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

from ibapi.contract import Contract
import threading
import time

class IBApi(EWrapper, EClient):
    def __init__(self, bot):
        EClient.__init__(self, self)
        self.is_connected = False
        self.bot = bot

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
            self.bot.on_price_update(price)

class Bot:
    ib = None
    market_data_requested = False
    position = 0  # Initial position is flat
    symbol = ""

    def __init__(self):
        self.ib = IBApi(self)
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)

        # -----------------------------------------Create IB contract object--------------------------------------
        self.symbol = input("Enter the symbol you want to trade: ")
        self.contract = Contract()
        self.contract.symbol = self.symbol.upper()
        self.contract.secType = "STK"
        self.contract.exchange = "SMART"
        self.contract.currency = "USD"

        # Switch market data type to delayed (Type 3)
        self.ib.reqMarketDataType(3)

        # Request Market Data
        self.request_market_data()

    def request_market_data(self):
        if not self.market_data_requested:
            self.ib.reqMktData(1, self.contract, "", False, False, [])
            self.market_data_requested = True

    def on_price_update(self, price):
        print("Current Price:", price)

        # Implement your trading strategy
        if price < 100 and self.position == 0:  # Buy condition
            print("Buy Signal!")
            self.place_order("BUY")
            self.position = 1  # Update position to long

        elif price > 120 and self.position == 1:  # Sell condition
            print("Sell Signal!")
            self.place_order("SELL")
            self.position = 0  # Update position to flat

    def place_order(self, action):
        # Implement your order placement logic here
        print(f"Placing {action} order for {self.symbol}")

    def run_loop(self):
        self.ib.connect("127.0.0.1", 7497, 1)
        self.ib.run()

# Start the Bot 
bot = Bot()
