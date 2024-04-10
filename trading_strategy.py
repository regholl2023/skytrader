import numpy as np

class TradingStrategy:
    def __init__(self):
        pass

    def calculate_sma(self, prices, window):
        """
        Calculate the Simple Moving Average (SMA) for the given price data over a specified window.

        :param prices: A list of prices (floats or integers).
        :param window: The window (number of periods) over which to calculate the SMA.
        :return: A list of SMA values, with 'None' for the positions where the SMA cannot be calculated due to insufficient data.
        """
        sma = [None] * (window - 1) + [np.mean(prices[i - window:i]) for i in range(window, len(prices) + 1)]
        return sma
        
    def generate_signals(self, historical_prices, sma_window=20, rsi_window=14, buy_threshold=70, sell_threshold=30):
        """
        Generate trading signals based on the provided historical prices and specified parameters.

        :param historical_prices: A list of historical prices (floats or integers).
        :param sma_window: The window (number of periods) for the SMA calculation. Default is 20.
        :param rsi_window: The window (number of periods) for the RSI calculation. Default is 14.
        :param buy_threshold: The RSI threshold above which a buy signal is generated. Default is 70.
        :param sell_threshold: The RSI threshold below which a sell signal is generated. Default is 30.
        :return: A list of trading signals, where 1 indicates a buy signal, -1 indicates a sell signal, and 0 indicates no signal.
        """
        signals = []

        # Calculate SMA
        short_sma = self.calculate_sma(historical_prices, sma_window)

        # Calculate RSI
        rsi_values = self.calculate_rsi(historical_prices, rsi_window)

        # Calculate MACD
        macd_line, signal_line, macd_histogram = self.calculate_macd(historical_prices)

        # Generate signals based on SMA, RSI, and MACD
        min_length = min(len(historical_prices), len(short_sma), len(rsi_values), len(macd_line))
        for i in range(min_length):
            if short_sma[i] is None or rsi_values[i] is None or macd_line[i] is None:
                signals.append(0)  # No signal if data is insufficient
            elif short_sma[i] > historical_prices[i] and rsi_values[i] > buy_threshold and macd_line[i] > signal_line[i]:
                signals.append(1)  # Buy signal
            elif short_sma[i] < historical_prices[i] and rsi_values[i] < sell_threshold and macd_line[i] < signal_line[i]:
                signals.append(-1)  # Sell signal
            else:
                signals.append(0)  # No signal

        return signals

    def calculate_macd(self, prices, short_window=12, long_window=26, signal_window=9):
        """
        Calculate the Moving Average Convergence Divergence (MACD) for the given price data.

        :param prices: A list of prices (floats or integers).
        :param short_window: The short EMA window. Default is 12.
        :param long_window: The long EMA window. Default is 26.
        :param signal_window: The signal line EMA window. Default is 9.
        :return: Three lists representing the MACD line, the signal line, and the MACD histogram.
        """
        # Calculate short EMA
        short_ema = self.calculate_ema(prices, short_window)
        
        # Calculate long EMA
        long_ema = self.calculate_ema(prices, long_window)
        
        # Ensure short and long EMAs have the same length
        min_length = min(len(short_ema), len(long_ema))
        short_ema = short_ema[:min_length]
        long_ema = long_ema[:min_length]
        
        # Calculate MACD line
        macd_line = np.subtract(short_ema, long_ema)
        
        # Calculate signal line
        signal_line = self.calculate_ema(macd_line, signal_window)
        
        # Ensure MACD line and signal line have the same length
        min_length = min(len(macd_line), len(signal_line))
        macd_line = macd_line[:min_length]
        signal_line = signal_line[:min_length]
        
        # Calculate MACD histogram
        macd_histogram = np.subtract(macd_line, signal_line)
        
        return macd_line, signal_line, macd_histogram
    
    def calculate_rsi(self, prices, window=14):
        """
        Calculate the Relative Strength Index (RSI) for the given price data.

        :param prices: A list of prices (floats or integers).
        :param window: The window (number of periods) over which to calculate the RSI. Default is 14.
        :return: A list of RSI values, with 'None' for the positions where the RSI cannot be calculated due to insufficient data.
        """
        deltas = np.diff(prices)
        up = deltas.clip(min=0)
        down = -deltas.clip(max=0)

        # Calculate the average gain and average loss
        avg_gain = np.mean(up[:window])
        avg_loss = np.mean(down[:window])

        rs = avg_gain / avg_loss if avg_loss != 0 else np.inf
        rsi = np.zeros_like(prices)
        rsi[:window] = 100.0 - 100.0 / (1.0 + rs)

        # Calculate RSI for the remaining periods
        for i in range(window, len(prices)):
            delta = deltas[i - 1]
            gain = up[i - 1] if delta > 0 else 0
            loss = down[i - 1] if delta < 0 else 0

            avg_gain = (avg_gain * (window - 1) + gain) / window
            avg_loss = (avg_loss * (window - 1) + loss) / window

            rs = avg_gain / avg_loss if avg_loss != 0 else np.inf
            rsi[i] = 100.0 - 100.0 / (1.0 + rs)

        return rsi
    
    




    def calculate_ema(self, prices, window):
        """
        Calculate the Exponential Moving Average (EMA) for the given price data over a specified window.

        :param prices: A list of prices (floats or integers).
        :param window: The window (number of periods) over which to calculate the EMA.
        :return: A list of EMA values.
        """
        ema = []
        if len(prices) < window:
            return ema  # Return an empty list if not enough data for calculation

        initial_sma = np.mean(prices[:window])
        ema.append(initial_sma)
        multiplier = 2 / (window + 1)  # EMA multiplier

        for price in prices[window:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])

        return ema

