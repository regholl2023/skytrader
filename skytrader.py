import pandas as pd
import numpy as np
import talib as ta
import alpaca_trade_api as tradeapi
import configparser
from typing import Tuple, List

class SkyTrader:
    def __init__(self, symbol: str, api_key: str, secret_key: str, base_url: str):
        self.symbol = symbol
        self.api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        self.rsi_period = 14  # Setting some default values, adjust as necessary
        self.sma_short_period = 20
        self.sma_long_period = 50
        self.atr_period = 14
        self.rsi_threshold = 30  # This is an example threshold
        self.initial_balance = 10000
        self.max_loss_per_trade = 0.02 * self.initial_balance  # Maximum 2% loss per trade
        self.position_size_percentage = 0.05  # This may not be used with dynamic sizing
        self.stop_loss_percentage = 0.02  # 2% stop loss
        
    def fetch_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        data = self.api.get_bars(
            self.symbol, tradeapi.TimeFrame.Day, start=start_date, end=end_date
        ).df
        return data

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        data['SMA_short'] = ta.SMA(data['close'].values, timeperiod=self.sma_short_period)
        data['SMA_long'] = ta.SMA(data['close'].values, timeperiod=self.sma_long_period)
        data['RSI'] = ta.RSI(data['close'].values, timeperiod=self.rsi_period)
        data['ATR'] = ta.ATR(data['high'].values, data['low'].values, data['close'].values, timeperiod=self.atr_period)
        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0
        signals.loc[(data['SMA_short'] > data['SMA_long']) & (data['RSI'] < self.rsi_threshold), 'signal'] = 1.0
        signals.loc[(data['SMA_short'] < data['SMA_long']) | (data['RSI'] > (100 - self.rsi_threshold)), 'signal'] = -1.0
        signals['positions'] = signals['signal'].diff()
        return signals

    def calculate_position_size(self, atr_value: float) -> float:
        """Calculate dynamic position size based on the ATR and a fixed risk per trade."""
        dollar_risk_per_trade = self.max_loss_per_trade
        dollar_risk_per_share = atr_value * self.stop_loss_percentage
        position_size = dollar_risk_per_trade / dollar_risk_per_share
        return position_size

    def backtest(self, data: pd.DataFrame, signals: pd.DataFrame) -> Tuple[float, int, int]:
        balance = self.initial_balance
        position = 0
        win_trades = 0
        loss_trades = 0
        is_position_open = False

        for i in range(1, len(signals)):
            atr_value = data['ATR'].iloc[i]
            position_size = self.calculate_position_size(atr_value)
            # Adjusting the number of shares to buy based on the dynamic position size and current price
            num_shares = position_size / data['close'].iloc[i]
            
            if signals['positions'].iloc[i] == 1.0 and not is_position_open:
                position = num_shares
                is_position_open = True
            elif signals['positions'].iloc[i] == -1.0 and is_position_open:
                balance += position * data['close'].iloc[i]  # Selling the position
                position = 0
                is_position_open = False
                # Assessing the trade outcome
                if balance > self.initial_balance:
                    win_trades += 1
                else:
                    loss_trades += 1

        # Closing any open position at the end of the backtest period
        if is_position_open:
            balance += position * data['close'].iloc[-1]
            is_position_open = False

        total_return = (balance - self.initial_balance) / self.initial_balance * 100
        return balance, win_trades, loss_trades

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config['alpaca']['api_key']
    secret_key = config['alpaca']['secret_key']
    base_url = config['alpaca']['base_url']

    symbol = input("Enter the ticker symbol (e.g., AAPL): ").upper()
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

    bot = SkyTrader(symbol, api_key, secret_key, base_url)
    data = bot.fetch_data(start_date, end_date)
    data_with_indicators = bot.calculate_indicators(data)
    signals = bot.generate_signals(data_with_indicators)
    final_balance, win_trades, loss_trades = bot.backtest(data_with_indicators, signals)

    print(f"Final Balance: {final_balance}")
    print(f"Winning Trades: {win_trades}, Losing Trades: {loss_trades}")

if __name__ == "__main__":
    main()
