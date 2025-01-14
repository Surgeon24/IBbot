from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from threading import Timer

class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.is_connected = False
        self.price_history = []
        self.currency_balances = {}

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
            self.price_history.append(price)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.start()
        self.nextOrderId = orderId
        print('The next valid order id is: ', self.nextOrderId)

    def createContract(self, symbol):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        print("contract created! symbol: ", symbol)
        return contract

    def sendOrder(self, contract, action):
        #Create order object
        order = Order()
        order.action = action
        order.totalQuantity = 10
        order.orderType = 'MKT'
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        #Place order
        self.placeOrder(self.nextOrderId, contract, order)
        return True
    
    def get_currency_balances(self):
        return self.currency_balances

    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        if contract.secType == "STK":  # Только акции
            print(f"Portfolio - Symbol: {contract.symbol}, Position: {position}, "
                  f"MarketPrice: {marketPrice}, MarketValue: {marketValue}, AverageCost: {averageCost}")

    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        if key in ["CashBalance"]:  # Интересующие ключи
            print(f"Account Value - {key}: {val} {currency}")
            self.currency_balances[currency] = {"value": val}

    def updateAccountTime(self, timeStamp: str):
        pass  # Если не нужно, оставляем пустым

    def accountDownloadEnd(self, accountName: str):
        print(f"Account Download Complete for {accountName}")

    def start(self):
        self.reqAccountUpdates(True, "")

    def stop(self):
        self.reqAccountUpdates(False, "")
        self.done = True
        self.disconnect()