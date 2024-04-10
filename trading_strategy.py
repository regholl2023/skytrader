import numpy as np

class TradingStrategy:
    def __init__(self):
        pass

    def calculate_macd(self, prices, short_window=12, long_window=26, signal_window=9):
        short_ema = self.calculate_ema(prices, short_window)
        long_ema = self.calculate_ema(prices, long_window)

        if short_ema is None or long_ema is None:
            return None, None, None

        macd_line = np.subtract(short_ema, long_ema)
        signal_line = self.calculate_ema(macd_line, signal_window)

        if signal_line is None:
            return None, None, None

        macd_histogram = np.subtract(macd_line[-len(signal_line):], signal_line)

        return macd_line, signal_line, macd_histogram

    def calculate_ema(self, prices, window):
        if len(prices) < window:
            return None

        weights = np.exp(np.linspace(-1., 0., window))
        weights /= weights.sum()

        ema = np.convolve(prices, weights, mode='valid')
        return ema
    
    
    def calculate_sma(self, prices, window=20):
        # Calculate SMA
        sma_values = []
        for i in range(len(prices) - window + 1):
            window_prices = prices[i:i + window]
            sma = sum(window_prices) / window
            sma_values.append(sma)
        return sma_values

    def generate_sma_crossover_signals(self, sma_short, sma_long):
        """
        Generate trading signals based on SMA crossover strategy.

        :param sma_short: List of short-term SMA values.
        :param sma_long: List of long-term SMA values.
        :return: List of trading signals (1 for buy signal, -1 for sell signal, 0 for hold).
        """
        signals = []
        min_length = min(len(sma_short), len(sma_long))  # Determine the minimum length of the SMA lists

        # Generate signals based on crossover strategy
        for i in range(1, min_length):
            if sma_short[i] > sma_long[i] and sma_short[i - 1] <= sma_long[i - 1]:
                signals.append(1)  # Buy signal
            elif sma_short[i] < sma_long[i] and sma_short[i - 1] >= sma_long[i - 1]:
                signals.append(-1)  # Sell signal
            else:
                signals.append(0)  # Hold signal

        return signals
        
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
    

    def calculate_macd(self, prices, short_window=12, long_window=26, signal_window=9):
        """
        Calculate the Moving Average Convergence Divergence (MACD) line, signal line, and MACD histogram.

        :param prices: A list of historical prices (floats or integers).
        :param short_window: The window (number of periods) for the short-term EMA. Default is 12.
        :param long_window: The window (number of periods) for the long-term EMA. Default is 26.
        :param signal_window: The window (number of periods) for the signal line EMA. Default is 9.
        :return: Three lists representing the MACD line, signal line, and MACD histogram, respectively.
        """
        # Calculate short-term EMA
        short_ema = self.calculate_ema(prices, short_window)
        
        # Calculate long-term EMA with the same window size as short-term EMA
        long_ema = self.calculate_ema(prices, short_window)  # Use short_window here
        
        # Debugging: Print lengths of short_ema and long_ema
        print("Length of short_ema:", len(short_ema))
        print("Length of long_ema:", len(long_ema))
        
        # Check if EMA calculations are valid
        if short_ema is None or long_ema is None:
            return None, None, None

        # Calculate MACD line
        macd_line = np.subtract(short_ema, long_ema)
        
        # Calculate signal line with the same window size as MACD line
        signal_line = self.calculate_ema(macd_line, len(macd_line))  # Use length of macd_line here
        
        # Check if signal line calculation is valid
        if signal_line is None:
            return None, None, None
        
        # Calculate MACD histogram
        macd_histogram = np.subtract(macd_line, signal_line)
        
        return macd_line, signal_line, macd_histogram


