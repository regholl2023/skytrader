import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import alpaca_trade_api as tradeapi
import configparser
import numpy as np

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
    historical_data = pd.DataFrame({'close': historical_data['close']}, index=historical_data.index.to_series())

    # Extract date from index and set it as the new index
    historical_data['date'] = pd.to_datetime(historical_data.index).date
    historical_data.set_index('date', inplace=True)

    # Calculate Moving Averages
    def calculate_moving_averages(data):
        data['short_moving_avg'] = data['close'].rolling(window=short_window, min_periods=1).mean()
        data['long_moving_avg'] = data['close'].rolling(window=long_window, min_periods=1).mean()

    # Define Trading Logic for Moving Average Crossover Strategy
    def moving_average_crossover_strategy(data):
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0  # Initialize signal column with 0s

        # Generate buy signals (Golden Cross)
        signals.iloc[short_window:, signals.columns.get_loc('signal')] = np.where(data['short_moving_avg'][short_window:] > data['long_moving_avg'][short_window:], 1.0, 0.0)

        # Generate sell signals (Death Cross)
        signals.iloc[short_window:, signals.columns.get_loc('signal')] = np.where(data['short_moving_avg'][short_window:] < data['long_moving_avg'][short_window:], -1.0, 0.0)

        return signals

    # Execute Trades
    def execute_trades(data, signals):
        data['buy_signal'] = np.where((signals['signal'].shift(1) == 0) & (signals['signal'] == 1), 1, 0)
        data['sell_signal'] = np.where((signals['signal'].shift(1) == 0) & (signals['signal'] == -1), -1, 0)

        # Initialize variables for backtesting
        position = 0  # Position in the market (0 = no position, 1 = long position, -1 = short position)
        initial_cash = 100000  # Initial cash amount
        cash = initial_cash  # Current cash balance
        portfolio_value = initial_cash  # Portfolio value
        shares = 0  # Number of shares held
        position_value = 0  # Value of current position
        trades = 0  # Number of trades executed
        wins = 0  # Number of winning trades

        # Iterate over each row in the DataFrame
        for index, row in data.iterrows():
            # Buy signal
            if row['buy_signal'] == 1:
                if position == 0:  # If not already in a position
                    shares = cash / row['close']  # Buy as many shares as possible with available cash
                    position = 1  # Enter long position
                    position_value = shares * row['close']  # Update position value
                    cash = 0  # Update cash balance
                    portfolio_value = position_value  # Update portfolio value
                    trades += 1  # Increment trades count

            # Sell signal
            elif row['sell_signal'] == -1:
                if position == 1:  # If in a long position
                    cash = shares * row['close']  # Sell all shares at current price
                    position = 0  # Exit position
                    shares = 0  # Reset shares held
                    position_value = 0  # Reset position value
                    portfolio_value = cash  # Update portfolio value
                    trades += 1  # Increment trades count
                    if cash > initial_cash:  # Check if the trade was profitable
                        wins += 1  # Increment wins count

            # Update portfolio value for remaining time periods
            else:
                portfolio_value = cash if position == 0 else shares * row['close']

            # Update DataFrame with portfolio value for each time period
            data.at[index, 'portfolio_value'] = portfolio_value

        # Calculate performance metrics
        total_return = (portfolio_value - initial_cash) / initial_cash * 100
        daily_returns = data['portfolio_value'].pct_change().dropna()
        sharpe_ratio = 0  # Default value
        if daily_returns.std() != 0:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        cum_portfolio_value = data['portfolio_value'].cummax()
        drawdown = (data['portfolio_value'] - cum_portfolio_value) / cum_portfolio_value
        max_drawdown = drawdown.min() * 100
        win_rate = (wins / trades) * 100 if trades > 0 else 0


        # Print performance metrics
        print("Total Return:", total_return, "%")
        print("Sharpe Ratio:", sharpe_ratio)
        print("Maximum Drawdown:", max_drawdown, "%")
        print("Win Rate:", win_rate, "%")

        return data

    # Example usage:
    # 1. Calculate moving averages
    calculate_moving_averages(historical_data)

    # 2. Define trading signals based on moving average crossover strategy
    signals = moving_average_crossover_strategy(historical_data)

    # 3. Execute trades based on signals and calculate performance metrics
    backtest_results = execute_trades(historical_data, signals)

    # Print backtest results
    print(backtest_results)

except tradeapi.rest.APIError as e:
    print("Error:", e)
