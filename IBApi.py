from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

class IBApi(EWrapper, EClient):
    def __init__(self, bot):
        EClient.__init__(self, self)
        self.is_connected = False
        self.bot = bot
        self.price_history = []

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
            self.bot.onPriceUpdate(price)
            self.price_history.append(price)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextOrderId = orderId
        # print('The next valid order id is: ', self.nextOrderId)

    def createContract(self, symbol):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
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