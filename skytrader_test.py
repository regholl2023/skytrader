import pandas as pd
import alpaca_trade_api as tradeapi
import configparser
import numpy as np
import talib as ta

# Load API keys from configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize Alpaca API client
api = tradeapi.REST(
    key_id=config['alpaca']['api_key'],
    secret_key=config['alpaca']['secret_key'],
    base_url=config['alpaca']['base_url']
)

symbol = "AAPL"
start_date = "2022-01-01"
end_date = "2022-12-31"
timeframe = "1D"
short_window = 50  # Define short window size
long_window = 200  # Define long window size

try:
    # Fetch historical market data
    historical_data = api.get_bars(symbol, timeframe, start=start_date, end=end_date).df

    # Create a DataFrame with the closing price as a column and the time column as the index
    historical_data = pd.DataFrame({'close': historical_data['close'], 'high': historical_data['high'], 'low': historical_data['low']}, index=historical_data.index.to_series())

    # Extract date from index and set it as the new index
    historical_data['date'] = pd.to_datetime(historical_data.index).date
    historical_data.set_index('date', inplace=True)

    # Calculate Moving Averages
    def calculate_moving_averages(data):
        data['short_moving_avg'] = data['close'].rolling(window=short_window, min_periods=1).mean()
        data['long_moving_avg'] = data['close'].rolling(window=long_window, min_periods=1).mean()

    # Define Trading Logic for Trend Following Strategy
    def trend_following_strategy(data):
        # Calculate moving averages
        calculate_moving_averages(data)

        # Calculate MACD
        data['macd'], data['macd_signal'], data['macd_hist'] = ta.MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9)

        # Calculate RSI
        data['rsi'] = ta.RSI(data['close'], timeperiod=14)

        # Calculate Bollinger Bands
        data['bb_upper'], data['bb_middle'], data['bb_lower'] = ta.BBANDS(data['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

        # Define thresholds for buy and sell signals
        buy_threshold_macd = 0.0  # Example: Buy when MACD line crosses above signal line
        sell_threshold_macd = 0.0  # Example: Sell when MACD line crosses below signal line

        buy_threshold_rsi = 30.0  # Example: Buy when RSI crosses above 30
        sell_threshold_rsi = 70.0  # Example: Sell when RSI crosses below 70

        buy_threshold_bb = data['bb_middle'] + data['bb_lower'] * 0.05  # Example: Buy when price crosses above lower Bollinger Band
        sell_threshold_bb = data['bb_middle'] + data['bb_upper'] * 0.05  # Example: Sell when price crosses below upper Bollinger Band

        # Generate buy signals (e.g., when short MA crosses above long MA, MACD crosses above signal line, etc.)
        # Example:
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0  # Initialize signal column with 0s

        signals['buy'] = ((data['macd'] > data['macd_signal']) & (data['rsi'] < buy_threshold_rsi)) | (data['close'] > data['bb_lower'])
        signals['sell'] = ((data['macd'] < data['macd_signal']) & (data['rsi'] > sell_threshold_rsi)) | (data['close'] < data['bb_upper'])

        return signals

    # Execute Trades
    def execute_trades(data, signals):
        # Place your trading logic here
        # Buy when signal is 1, sell when signal is -1

        return data

    # Example usage:
    # 1. Calculate moving averages
    calculate_moving_averages(historical_data)

    # 2. Define trading signals based on trend following strategy
    signals = trend_following_strategy(historical_data)

    # 3. Execute trades based on signals
    backtest_results = execute_trades(historical_data, signals)

    # Print backtest results
    print(backtest_results)

except tradeapi.rest.APIError as e:
    print("Error:", e)