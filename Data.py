import json
import time

class Data:
    account_value = {}
    account_stocks = {}
    bots_data = {}
    
    def __init__(self):
        pass

    def error(self, reqId, errorCode, errorString, advancedOrderReject=""):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def add_bot(self, thread_id, symbol, strategy):
        self.bots_data[thread_id] = {"symbol": symbol, "strategy": strategy}

    def remove_bot(self, thread_id):
        if thread_id in self.bots_data:
            del self.bots_data[thread_id]

    def remove_all_bots(self):
        self.bots_data.clear()

    async def send_bots_data(self, websocket):
        print("\nsending bots data!\n")
        await websocket.send(json.dumps(self.bots_data))

    async def send_account_data(self, websocket, ib):
        activeStrategies = len(self.bots_data)
        # time.sleep(1)
        accountValue = ib.get_currency_balances()
        # accountValue["Net"] = {"value": ?, "currency": ??}
        account_data = {
            "accountValue": accountValue,
            "activeStrategies": activeStrategies,
            "accepted": 000,
            "own": 000
        }
        await websocket.send(json.dumps(account_data))

