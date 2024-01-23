import ibapi
from ibapi.client import EClient
from ibapi.common import TickerId
from ibapi.wrapper import EWrapper

from ibapi.contract import Contract
from ibapi.order import *
import threading
import time


class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self,self)

    def realtimeBar(self, reqId: TickerId, time: int, open_: float, high: float, low: float, close: float, volume: int, wap: float, count: int):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        try:
            bot.on_bar_update(reqId, time, open_, high, low, close, volume, wap, count)
        except Exception as e:
            print(e)
    def error(self, id, errorCode, errorMsg):
        print(errorCode)
        print(errorMsg)

class Bot:
    ib = None
    def __init__(self):

        self.ib = IBApi()
        self.ib.connect("127.0.0.1", 7497,1)
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)

        symbol = input("Enter the symbol: ")

        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        self.ib.reqMarketDataType(3)
        self.ib.reqRealTimeBars(0, contract, 5, "TRADES", 1, [])




    def run_loop(self):
        self.ib.run()

    def on_bar_update(self, reqId, time, open_, high, low, close, volume, wap, count):
        print(close)

bot = Bot()
    























# import ibapi
# from ibapi.client import EClient
# from ibapi.common import TickerId
# from ibapi.wrapper import EWrapper

# from ibapi.contract import Contract
# from ibapi.order import *
# import threading
# import time

# class IBApi(EWrapper, EClient):
#     def __init__(self):
#         EClient.__init__(self, self)
#         self.connected = False

#     def realtimeBar(self, reqId: TickerId, time: int, open_: float, high: float, low: float, close: float, volume: int, wap: float, count: int):
#         super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
#         try:
#             bot.on_bar_update(reqId, time, open_, high, low, close, volume, wap, count)
#         except Exception as e:
#             print(e)

#     def error(self, id, errorCode, errorMsg):
#         if errorCode == 1102:  # Connectivity between IB and TWS has been lost
#             print("Warning: Connectivity between IB and TWS has been lost.")
#             self.connected = False
#         elif errorCode == 504:  # Not connected
#             print("Error 504: Not connected to the server.")
#             self.connected = False
#         else:
#             print(f"Error {errorCode}: {errorMsg}")

# class Bot:
#     ib = None

#     def __init__(self):
#         self.ib = IBApi()
#         self.ib.connect("127.0.0.1", 7497, 1)

#         ib_thread = threading.Thread(target=self.run_loop, daemon=True)
#         ib_thread.start()
#         while not self.ib.connected:
#             time.sleep(1)

#         symbol = input("Enter the symbol: ")

#         contract = Contract()
#         contract.symbol = symbol.upper()
#         contract.secType = "STK"
#         contract.exchange = "SMART"
#         contract.currency = "USD"

#         self.ib.reqRealTimeBars(0, contract, 5, "TRADES", 1, [])

#     def run_loop(self):
#         self.ib.run()
#         time.sleep(1)  # Add a small delay after the event loop

#     def on_bar_update(self, reqId, time, open_, high, low, close, volume, wap, count):
#         print(close)

# bot = Bot()
