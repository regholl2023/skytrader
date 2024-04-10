import numpy as np

def calculate_sma(prices, window):
    """
    Calculate the Simple Moving Average (SMA) for the given price data over a specified window.

    :param prices: A list of prices (floats or integers).
    :param window: The window (number of periods) over which to calculate the SMA.
    :return: A list of SMA values, with 'None' for the positions where the SMA cannot be calculated due to insufficient data.
    """
    sma = [None] * (window - 1) + [np.mean(prices[i - window:i]) for i in range(window, len(prices) + 1)]
    return sma

def calculate_rsi(prices, window=14):
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
