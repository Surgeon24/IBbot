from ibapi.client import *
from ibapi.wrapper import *


class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        mycontract = Contract()
        mycontract.symbol = "AAPL"
        mycontract.secType = "STK"
        mycontract.exchange = "SMART"
        mycontract.currency = "USD"

        self.reqMarketDataType(4)
        self.reqMktData(orderId, mycontract, "", 0, 0, [])
    
    def tickPrice(self, reqId, tickType, price, attrib):
        print(f"tickPrice. reqId: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, price: {price}, attribs: {attrib}")

    def tickSize(self, reqId, tickType, size):
        print(f"tickSize. reqId: {reqId}, tickType: {TickTypeEnum.to_str(tickType)}, size: {size}")


bot = IBApi()
bot.connect("127.0.0.1", 7497, 1000)
bot.run()

