"""
Простая торговая стратегия на основе ценовой истории.
Аргументы:
- price_history: список последних цен закрытия, где цены упорядочены по возрастанию времени.
Возвращает:
- action: действие, которое необходимо выполнить (BUY - покупка, SELL - продажа, HOLD - держать позицию).
"""
from statistics import mean, stdev
class StrategyAdapter:

    def runStrategy(self, id, price_history):
        print("strat:", id)
        match id:
            case '1':
                return self.strategy1(price_history)
            case '2':
                return self.strategy2(price_history)
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
        if len(price_history) < 20:
            print("length of history price = ", len(price_history))
            return "HOLD"  # Если данных недостаточно, удерживаем позицию

        # Параметры для Bollinger Bands и Stochastic
        bb_length = 20
        bb_multiplier = 2.0
        stoch_k = 14
        stoch_d = 3
        stoch_smooth_k = 3
        stoch_smooth_d = 3

        # Расчёт Bollinger Bands
        middle_bb = mean(price_history[-bb_length:])
        upper_bb = middle_bb + bb_multiplier * stdev(price_history[-bb_length:])
        lower_bb = middle_bb - bb_multiplier * stdev(price_history[-bb_length:])

        # Расчёт Stochastic Oscillator
        high_prices = [max(price_history[i - stoch_k:i]) for i in range(stoch_k, len(price_history) + 1)]
        low_prices = [min(price_history[i - stoch_k:i]) for i in range(stoch_k, len(price_history) + 1)]
        closes = price_history[-len(high_prices):]
        k_values = [(close - low) / (high - low) * 100 if high - low != 0 else 50 
                    for close, high, low in zip(closes, high_prices, low_prices)]
        smoothed_k = mean(k_values[-stoch_smooth_k:])
        smoothed_d = mean(k_values[-stoch_smooth_d:])

        # Условия стратегии
        current_price = price_history[-1]

        if current_price < lower_bb and smoothed_k < 20:
            return "BUY"
        elif current_price > upper_bb and smoothed_k > 80:
            return "SELL"
        elif current_price > middle_bb and smoothed_k < smoothed_d:
            return "SELL"
        elif current_price < middle_bb and smoothed_k > smoothed_d:
            return "BUY"

        return "HOLD"

    # def strategy2(self, price_history):
    #     # Проверяем, что у нас есть достаточно данных для анализа
    #     if len(price_history) < 3:
    #         print("length of history price = ", len(price_history))
    #         return "HOLD"  # Если данных недостаточно, держим позицию
    #     # Получаем последние две цены закрытия
    #     last_two_prices = price_history[-2:]
    #     if (last_two_prices[0] < last_two_prices[1]):
    #         return "HOLD"
    #     if (last_two_prices[0] > last_two_prices[1]):
    #         return "SELL"
    #     return "HOLD"