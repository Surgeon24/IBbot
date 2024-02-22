"""
Простая торговая стратегия на основе ценовой истории.
Аргументы:
- price_history: список последних цен закрытия, где цены упорядочены по возрастанию времени.
Возвращает:
- action: действие, которое необходимо выполнить (BUY - покупка, SELL - продажа, HOLD - держать позицию).
"""
class StrategyAdapter:

    def runStrategy(self, id, price_history):
        print("strat:", id)
        match id:
            case 1:
                return self.strategy1(price_history)
            case 2:
                print("case 2")
                tmp = self.strategy2(price_history)
                print(tmp)
                return tmp
            case _:
                print("Unhandled id:", id)

    def strategy1(self, price_history):
        # Проверяем, что у нас есть достаточно данных для анализа
        if len(price_history) < 4:
            print("length of history price = ", len(price_history))
            return "HOLD"  # Если данных недостаточно, держим позицию
        # Получаем последние три цены закрытия
        last_three_prices = price_history[-3:]
        # Проверяем условие для покупки
        if all(last_three_prices[i] < last_three_prices[i + 1] for i in range(2)):
            return "BUY"
        # Проверяем условие для продажи
        if all(last_three_prices[i] > last_three_prices[i + 1] for i in range(2)):
            return "SELL"
        return "HOLD"
    
    def strategy2(self, price_history):
        # Проверяем, что у нас есть достаточно данных для анализа
        if len(price_history) < 3:
            print("length of history price = ", len(price_history))
            return "HOLD"  # Если данных недостаточно, держим позицию
        # Получаем последние две цены закрытия
        last_two_prices = price_history[-2:]
        if (last_two_prices[i] < last_two_prices[i + 1]):
            return "HOLD"
        if (last_two_prices[i] > last_two_prices[i + 1]):
            return "SELL"
        return "HOLD"