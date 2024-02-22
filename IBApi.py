import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

from ibapi.contract import Contract
from ibapi.order import *
import threading
import time


# Class for connection
class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self) 
    # Listen for rt bars
    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        try:
            bot.on_bar_update(reqId, time, open_, high, low, close, volume, wap, count)
        except Exception as e:
            print(e)
    def error(self, id, errorCode, errorMsg):
        print(errorCode)
        print(errorMsg)
# Class for bot logic
class Bot:
    ib = None
    def __init__(self):
        self.ib = IBApi()
        self.ib.connect("127.0.0.1", 7497, 1)
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)
        symbol = input("Enter the symbol you whant to trade: ")
        # Create our IB contract object
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        # Request Market Data
        self.ib.reqRealTimeBars(0, contract, 5, "TRADES", 1, [])


    # listen to socket in separate thread    
    def run_loop(self):
        self.ib.run()
    # pass rt bar data back to our  bot object
    def on_bar_update(self, reqId, time, open_, high, low, close, volume, wap, count):
        print(close)

# Start the Bot
bot = Bot()