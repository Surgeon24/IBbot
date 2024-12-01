from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Timer

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    # def error(self, reqId, errorCode, errorString, advancedOrderReject=""):
    #     print("Error: ", reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId):
        self.start()

    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        if contract.secType == "STK":  # Только акции
            print(f"Portfolio - Symbol: {contract.symbol}, Position: {position}, "
                  f"MarketPrice: {marketPrice}, MarketValue: {marketValue}, AverageCost: {averageCost}")

    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        if key in ["NetLiquidation", "CashBalance"]:  # Интересующие ключи
            print(f"Account Value - {key}: {val} {currency} (Account: {accountName})")

    # def updateAccountTime(self, timeStamp: str):
    #     pass  # Если не нужно, оставляем пустым

    # def accountDownloadEnd(self, accountName: str):
    #     print(f"Account Download Complete for {accountName}")

    def start(self):
        self.reqAccountUpdates(True, "")

    def stop(self):
        self.reqAccountUpdates(False, "")
        self.done = True
        self.disconnect()

app = TestApp()
app.connect("127.0.0.1", 7497, 1)
Timer(1, app.stop).start()
app.run()
