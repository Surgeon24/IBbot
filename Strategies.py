"""
Простая торговая стратегия на основе ценовой истории.
Аргументы:
- price_history: список последних цен закрытия, где цены упорядочены по возрастанию времени.
Возвращает:
- action: действие, которое необходимо выполнить (BUY - покупка, SELL - продажа, HOLD - держать позицию).
"""
from statistics import mean, stdev
import numpy as np

class StrategyAdapter:
    sma_length = 14
    sma_length_fast = 9
    sma_length_slow = 21
    rsi_length = 14
    macd_fast = 12
    macd_slow = 26
    adx_length = 14

    def runStrategy(self, id, price_history, params):
        print("strategy id:", id)
        self.update_params(params)
        match id:
            case '1':
                return self.sma_strategy(price_history)
            case '2':
                return self.investing_strategy(price_history)
            case _:
                print("Unhandled id:", id)    

    def update_params(self, params):
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: {key} is not a recognized parameter.")

    def sma(data, length):
        """Вычисляет простую скользящую среднюю (SMA)."""
        if len(data) < length:
            return None
        return np.mean(data[-length:])

    def rsi(data, length):
        """Вычисляет индекс относительной силы (RSI)."""
        if len(data) < length:
            return None
        deltas = np.diff(data)
        gains = np.where(deltas > 0, deltas, 0)
        losses = -np.where(deltas < 0, deltas, 0)
        avg_gain = np.mean(gains[-length:])
        avg_loss = np.mean(losses[-length:])
        if avg_loss == 0:
            return 100  # Если нет потерь, RSI равен 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def macd(data, fast_length, slow_length, signal_length):
        """Вычисляет MACD и сигнальную линию."""
        if len(data) < slow_length:
            return None, None
        ema_fast = np.mean(data[-fast_length:])
        ema_slow = np.mean(data[-slow_length:])
        macd_line = ema_fast - ema_slow
        if len(data) < (slow_length + signal_length - 1):
            return macd_line, None
        signal_line = np.mean(data[-signal_length:])
        return macd_line, signal_line
    
    def adx(high, low, close, length):
        if len(close) < length + 1:
            return None
        up_move = [high[i] - high[i - 1] for i in range(1, len(high))]
        down_move = [low[i - 1] - low[i] for i in range(1, len(low))]
        plus_dm = [max(up, 0) if up > down else 0 for up, down in zip(up_move, down_move)]
        minus_dm = [max(down, 0) if down > up else 0 for up, down in zip(up_move, down_move)]
        true_range = [max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])) for i in range(1, len(close))]
        
        plus_di = [(sum(plus_dm[i - length:i]) / sum(true_range[i - length:i])) * 100 for i in range(length, len(close))]
        minus_di = [(sum(minus_dm[i - length:i]) / sum(true_range[i - length:i])) * 100 for i in range(length, len(close))]
        dx = [abs(plus - minus) / (plus + minus) * 100 for plus, minus in zip(plus_di, minus_di)]
        adx_value = sum(dx[-length:]) / length
        return adx_value

    def ema(data, length):
        if len(data) < length:
            return []
        ema_values = [sum(data[:length]) / length]
        multiplier = 2 / (length + 1)
        for price in data[length:]:
            ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
        return ema_values

                                                    # strategies
    def sma_strategy(self, price_history, sma_length=14):
        """
        Торговая стратегия на основе простой скользящей средней (SMA).
        
        price_history: Список цен закрытия, упорядоченных по времени (от старых к новым).
        sma_length: Период для расчета SMA.
        return: Сигнал "BUY", "SELL" или "HOLD".
        """
        # Проверяем, достаточно ли данных для расчета SMA
        if len(price_history) < sma_length:
            print(f"Not enough data: {len(price_history)} / {sma_length}")
            return "HOLD"
        
        # Вычисляем SMA как среднее последних `sma_length` цен
        sma_value = sum(price_history[-sma_length:]) / sma_length
        
        # Сравниваем последнюю цену с SMA
        last_price = price_history[-1]
        if last_price > sma_value:
            return "BUY"
        elif last_price < sma_value:
            return "SELL"
        else:
            return "HOLD"

    # Пример использования
    # price_history = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113]  # Пример данных
    # signal = sma_strategy(price_history, sma_length=14)
    # print("Торговый сигнал:", signal)


    # def strategy1(self, price_history):
    #     # Проверяем, что у нас есть достаточно данных для анализа
    #     if len(price_history) < 4:
    #         print("length of history price = ", len(price_history))
    #         return "HOLD"  # Если данных недостаточно, держим позицию
    #     # Получаем последние три цены закрытия
    #     last_three_prices = price_history[-3:]
    #     # Проверяем условие для покупки
    #     if all(last_three_prices[i] < last_three_prices[i + 1] for i in range(2)):
    #         return "BUY"
    #     # Проверяем условие для продажи
    #     if all(last_three_prices[i] > last_three_prices[i + 1] for i in range(2)):
    #         return "SELL"
    #     return "HOLD"

    def investing_strategy(price_history, sma_length_fast=9, sma_length_slow=21, 
                rsi_length=14, rsi_neutral=20, 
                macd_fast=12, macd_slow=26, macd_signal=9):
        """
        Торговая стратегия с использованием SMA, RSI и MACD.
        
        :param price_history: Список цен закрытия.
        :return: Сигнал "BUY", "SELL", "CLOSE_LONG", "CLOSE_SHORT" или "HOLD".
        """
        if len(price_history) < max(sma_length_slow, rsi_length, macd_slow + macd_signal - 1):
            print("Недостаточно данных для расчета всех индикаторов.")
            return "HOLD"
        
        # Вычисление индикаторов
        sma_fast = sma(price_history, sma_length_fast)
        sma_slow = sma(price_history, sma_length_slow)
        rsi_value = rsi(price_history, rsi_length)
        macd_line, signal_line = macd(price_history, macd_fast, macd_slow, macd_signal)

        # Условия длинной позиции
        if sma_fast and sma_slow and rsi_value and macd_line and signal_line:
            if sma_fast > sma_slow and rsi_value > rsi_neutral and macd_line > signal_line:
                return "BUY"
            if sma_fast < sma_slow or rsi_value < rsi_neutral or macd_line < signal_line:
                return "CLOSE_LONG"
            if sma_fast < sma_slow and rsi_value < rsi_neutral and macd_line < signal_line:
                return "SELL"
            if sma_fast > sma_slow or rsi_value > rsi_neutral or macd_line > signal_line:
                return "CLOSE_SHORT"
        
        return "HOLD"

    # Пример использования
    # price_history = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113]
    # signal = strategy(price_history)
    # print("Торговый сигнал:", signal)

    # def strategy2(self, price_history):
    #     if len(price_history) < 20:
    #         print("length of history price = ", len(price_history))
    #         return "HOLD"  # Если данных недостаточно, удерживаем позицию

    #     # Параметры для Bollinger Bands и Stochastic
    #     bb_length = 20
    #     bb_multiplier = 2.0
    #     stoch_k = 14
    #     stoch_d = 3
    #     stoch_smooth_k = 3
    #     stoch_smooth_d = 3

    #     # Расчёт Bollinger Bands
    #     middle_bb = mean(price_history[-bb_length:])
    #     upper_bb = middle_bb + bb_multiplier * stdev(price_history[-bb_length:])
    #     lower_bb = middle_bb - bb_multiplier * stdev(price_history[-bb_length:])

    #     # Расчёт Stochastic Oscillator
    #     high_prices = [max(price_history[i - stoch_k:i]) for i in range(stoch_k, len(price_history) + 1)]
    #     low_prices = [min(price_history[i - stoch_k:i]) for i in range(stoch_k, len(price_history) + 1)]
    #     closes = price_history[-len(high_prices):]
    #     k_values = [(close - low) / (high - low) * 100 if high - low != 0 else 50 
    #                 for close, high, low in zip(closes, high_prices, low_prices)]
    #     smoothed_k = mean(k_values[-stoch_smooth_k:])
    #     smoothed_d = mean(k_values[-stoch_smooth_d:])

    #     # Условия стратегии
    #     current_price = price_history[-1]

    #     if current_price < lower_bb and smoothed_k < 20:
    #         return "BUY"
    #     elif current_price > upper_bb and smoothed_k > 80:
    #         return "SELL"
    #     elif current_price > middle_bb and smoothed_k < smoothed_d:
    #         return "SELL"
    #     elif current_price < middle_bb and smoothed_k > smoothed_d:
    #         return "BUY"

    #     return "HOLD"

    # def sma(data, length):
    #     """Вычисляет простую скользящую среднюю (SMA)."""
    #     if len(data) < length:
    #         return None
    #     return np.mean(data[-length:])

    # def rsi(data, length):
    #     """Вычисляет индекс относительной силы (RSI)."""
    #     if len(data) < length:
    #         return None
    #     deltas = np.diff(data)
    #     gains = np.where(deltas > 0, deltas, 0)
    #     losses = -np.where(deltas < 0, deltas, 0)
    #     avg_gain = np.mean(gains[-length:])
    #     avg_loss = np.mean(losses[-length:])
    #     if avg_loss == 0:
    #         return 100  # Если нет потерь, RSI равен 100
    #     rs = avg_gain / avg_loss
    #     return 100 - (100 / (1 + rs))

    # def macd(data, fast_length, slow_length, signal_length):
    #     """Вычисляет MACD и сигнальную линию."""
    #     if len(data) < slow_length:
    #         return None, None
    #     ema_fast = np.mean(data[-fast_length:])
    #     ema_slow = np.mean(data[-slow_length:])
    #     macd_line = ema_fast - ema_slow
    #     if len(data) < (slow_length + signal_length - 1):
    #         return macd_line, None
    #     signal_line = np.mean(data[-signal_length:])
    #     return macd_line, signal_line

    def adx_strategy(price_history, volumes, 
                                sma_length_fast=9, sma_length_slow=21,
                                rsi_length=14, rsi_overbought=70, rsi_oversold=30, 
                                macd_fast=12, macd_slow=26, macd_signal=9,
                                adx_length=14, adx_threshold=25, min_volume=1000, window_size=14):
        """
        Торговая стратегия с использованием SMA, RSI, MACD и ADX.
        
        :param price_history: Список цен закрытия.
        :param volumes: Список объемов.
        :param window_size: Размер окна для вычисления high/low.
        :return: Сигнал "BUY", "SELL", "CLOSE_LONG", "CLOSE_SHORT" или "HOLD".
        """
        if len(price_history) < max(sma_length_slow, rsi_length, macd_slow + macd_signal - 1, adx_length):
            print("Недостаточно данных для расчета всех индикаторов.")
            return "HOLD"
        
        # Вычисление индикаторов
        sma_fast = sma(price_history, sma_length_fast)
        sma_slow = sma(price_history, sma_length_slow)
        rsi_value = rsi(price_history, rsi_length)
        macd_line, signal_line = macd(price_history, macd_fast, macd_slow, macd_signal)
        high_prices = [max(price_history[max(0, i - window_size):i + 1]) for i in range(len(price_history))]
        low_prices = [min(price_history[max(0, i - window_size):i + 1]) for i in range(len(price_history))]
        adx_value = adx(high_prices, low_prices, price_history, adx_length)
        current_volume = volumes[-1]

        # Проверка условий
        if sma_fast and sma_slow and rsi_value and macd_line and signal_line and adx_value is not None:
            if current_volume >= min_volume:
                # Условия длинной позиции
                if sma_fast > sma_slow and rsi_value > rsi_oversold and macd_line > signal_line and adx_value > adx_threshold:
                    return "BUY"
                if sma_fast < sma_slow or rsi_value > rsi_overbought or macd_line < signal_line:
                    return "CLOSE_LONG"

                # Условия короткой позиции
                if sma_fast < sma_slow and rsi_value < rsi_overbought and macd_line < signal_line and adx_value > adx_threshold:
                    return "SELL"
                if sma_fast > sma_slow or rsi_value < rsi_oversold or macd_line > signal_line:
                    return "CLOSE_SHORT"

        return "HOLD"

























    # def atr(price_history, length):
    #     """ATR на основе цен закрытия."""
    #     if len(price_history) < length + 1:
    #         return None
    #     true_ranges = [abs(price_history[i] - price_history[i - 1]) for i in range(1, len(price_history))]
    #     return np.mean(true_ranges[-length:])

    # def trading_strategy(price_history, 
    #             sma_length_fast=5, sma_length_slow=10, 
    #             rsi_length=7, rsi_neutral=20, 
    #             macd_fast=6, macd_slow=13, macd_signal=5, 
    #             atr_length=14, atr_multiplier=1.5):
    #     """
    #     Торговая стратегия с использованием SMA, RSI, MACD и ATR.
        
    #     :param price_history: Список цен закрытия.
    #     :return: Сигнал "BUY", "SELL", "CLOSE_LONG", "CLOSE_SHORT" или "HOLD".
    #     """
    #     if len(price_history) < max(sma_length_slow, rsi_length, macd_slow + macd_signal - 1, atr_length + 1):
    #         print("Недостаточно данных для расчета всех индикаторов.")
    #         return "HOLD"

    #     # Вычисление индикаторов
    #     sma_fast = sma(price_history, sma_length_fast)
    #     sma_slow = sma(price_history, sma_length_slow)
    #     rsi_value = rsi(price_history, rsi_length)
    #     macd_line, signal_line = macd(price_history, macd_fast, macd_slow, macd_signal)
    #     atr_value = atr(price_history, atr_length)

    #     # Текущая цена
    #     current_price = price_history[-1]

    #     # Условия длинной позиции
    #     if sma_fast > sma_slow and rsi_value > rsi_neutral and macd_line > signal_line:
    #         stop_loss = current_price - atr_value * atr_multiplier
    #         take_profit = current_price + atr_value * atr_multiplier
    #         return "BUY", stop_loss, take_profit

    #     # Условия закрытия длинной позиции
    #     if sma_fast < sma_slow or rsi_value < rsi_neutral or macd_line < signal_line:
    #         return "CLOSE_LONG"

    #     # Условия короткой позиции
    #     if sma_fast < sma_slow and rsi_value < (100 - rsi_neutral) and macd_line < signal_line:
    #         stop_loss = current_price + atr_value * atr_multiplier
    #         take_profit = current_price - atr_value * atr_multiplier
    #         return "SELL", stop_loss, take_profit

    #     # Условия закрытия короткой позиции
    #     if sma_fast > sma_slow or rsi_value > (100 - rsi_neutral) or macd_line > signal_line:
    #         return "CLOSE_SHORT"

    #     return "HOLD"

# Пример использования
# price_history = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113]

# signal = strategy(price_history)
# print("Торговый сигнал:", signal)
