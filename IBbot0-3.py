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

        self.reqContractDetails(orderId, mycontract)
    
    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        print(contractDetails.contract)

        myorder = Order()
        myorder.orderId = reqId
        myorder.action = "BUY"
        myorder.orderType = "MKT"
        myorder.totalQuantity = 10

        self.placeOrder(reqId, contractDetails.contract, myorder)
        self.disconnect()

    # def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState):
    #     print(f"orderId: {orderId}, contract: {contract}, order: {order}")
    
    # def orderStatus(self, orderId: OrderId, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
    #     print(f"orderId: {orderId}, status: {status}, filled: {filled}, remaining: {remaining}, avgFillPrice: {avgFillPrice}...")

    # def execDetails(self, reqId: int, contract: Contract, execution: Execution):
    #     print(f"reqId: {reqId}, contract: {contract}, execution: {execution}")


bot = IBApi()
bot.connect("127.0.0.1", 7497, 1000)
bot.run()