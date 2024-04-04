import pandas as pd
import alpaca_trade_api as tradeapi
import configparser
import numpy as np
import talib as ta
import datetime

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

# Parameter grid for optimization
parameter_grid = {
    'short_window': [20, 50, 100],
    'long_window': [100, 200, 300],
    'macd_fastperiod': [8, 12, 16],
    'macd_slowperiod': [21, 26, 30],
    'macd_signalperiod': [7, 9, 11],
    'rsi_period': [10, 14, 18],
    'bb_nbdevup': [1.5, 2, 2.5],
    'bb_nbdevdn': [1.5, 2, 2.5]
}

# Fetch historical market data
historical_data = api.get_bars(symbol, timeframe, start=start_date, end=end_date).df

# Create a DataFrame with the closing price as a column and the time column as the index
historical_data = pd.DataFrame({'close': historical_data['close'], 'high': historical_data['high'], 'low': historical_data['low']}, index=historical_data.index.to_series())

# Extract date from index and set it as the new index
historical_data['date'] = pd.to_datetime(historical_data.index).date
historical_data.set_index('date', inplace=True)

# Calculate Moving Averages
def calculate_moving_averages(data, short_window, long_window):
    data['short_moving_avg'] = data['close'].rolling(window=short_window, min_periods=1).mean()
    data['long_moving_avg'] = data['close'].rolling(window=long_window, min_periods=1).mean()

# Define Trading Logic for Trend Following Strategy
def trend_following_strategy(data, short_window, long_window, macd_fastperiod, macd_slowperiod, macd_signalperiod, rsi_period, bb_nbdevup, bb_nbdevdn):
    # Calculate moving averages
    calculate_moving_averages(data, short_window, long_window)

    # Calculate MACD
    data['macd'], data['macd_signal'], data['macd_hist'] = ta.MACD(data['close'], fastperiod=macd_fastperiod, slowperiod=macd_slowperiod, signalperiod=macd_signalperiod)

    # Calculate RSI
    data['rsi'] = ta.RSI(data['close'], timeperiod=rsi_period)

    # Calculate Bollinger Bands
    data['bb_upper'], data['bb_middle'], data['bb_lower'] = ta.BBANDS(data['close'], timeperiod=20, nbdevup=bb_nbdevup, nbdevdn=bb_nbdevdn, matype=0)

    # Define thresholds for buy and sell signals
    buy_threshold_rsi = 30.0
    sell_threshold_rsi = 70.0

    # Generate buy and sell signals
    signals = pd.DataFrame(index=data.index)
    signals['buy'] = ((data['macd'] > data['macd_signal']) & (data['rsi'] < buy_threshold_rsi)) | (data['close'] > data['bb_lower'])
    signals['sell'] = ((data['macd'] < data['macd_signal']) & (data['rsi'] > sell_threshold_rsi)) | (data['close'] < data['bb_upper'])

    return signals

# Backtest the strategy with specific parameters
def backtest_strategy(data, parameters):
    signals = trend_following_strategy(data, **parameters)
    transaction_log = []
    balance = 10000  # Initial account balance
    commission_fee = 5  # Commission fee per transaction

    for i in range(1, len(data)):
        if signals['buy'].iloc[i] and not signals['buy'].iloc[i - 1]:
            if balance >= data['close'].iloc[i] + commission_fee:
                balance -= data['close'].iloc[i] + commission_fee
                transaction_log.append(('buy', data.index[i], data['close'].iloc[i]))
        elif signals['sell'].iloc[i] and not signals['sell'].iloc[i - 1]:
            balance += data['close'].iloc[i] - commission_fee
            transaction_log.append(('sell', data.index[i], data['close'].iloc[i]))

    total_return = ((balance - 10000) / 10000) * 100
    return total_return, transaction_log

# Grid search for best parameters
best_return = -float('inf')
best_parameters = None

for short_window in parameter_grid['short_window']:
    for long_window in parameter_grid['long_window']:
        for macd_fastperiod in parameter_grid['macd_fastperiod']:
            for macd_slowperiod in parameter_grid['macd_slowperiod']:
                for macd_signalperiod in parameter_grid['macd_signalperiod']:
                    for rsi_period in parameter_grid['rsi_period']:
                        for bb_nbdevup in parameter_grid['bb_nbdevup']:
                            for bb_nbdevdn in parameter_grid['bb_nbdevdn']:
                                parameters = {
                                    'short_window': short_window,
                                    'long_window': long_window,
                                    'macd_fastperiod': macd_fastperiod,
                                    'macd_slowperiod': macd_slowperiod,
                                    'macd_signalperiod': macd_signalperiod,
                                    'rsi_period': rsi_period,
                                    'bb_nbdevup': bb_nbdevup,
                                    'bb_nbdevdn': bb_nbdevdn
                                }
                                total_return, _ = backtest_strategy(historical_data, parameters)
                                if total_return > best_return:
                                    best_return = total_return
                                    best_parameters = parameters

print("Best Parameters:", best_parameters)
print("Best Return:", best_return)
