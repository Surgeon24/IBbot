from IBApi import IBApi

api = IBApi()
api.connect("127.0.0.1", 7497, 0)

# Дождаться завершения получения данных
import time
time.sleep(5)

# Получить балансы валют
balances = api.get_currency_balances()
print("Currency Balances:", balances)

api.disconnect()