import os
from alpaca_trade_api.rest import REST
from dotenv import load_dotenv

load_dotenv()  # This loads the .env file at the project root

class AlpacaIntegration:
    def __init__(self):
        self.api = REST(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), base_url='https://paper-api.alpaca.markets')
    
    def get_account_info(self):
        return self.api.get_account()

    def fetch_market_data(self, symbol, timeframe='1D', limit=100):
        # Fetch market data using the updated get_bars method
        bars = self.api.get_bars(symbol, timeframe, limit=limit)
        return bars

    def fetch_historical_prices(self, symbol, start_date, end_date, timeframe='1D'):
        """
        Fetch historical price data for a given symbol within a specified date range.

        :param symbol: The symbol to fetch data for.
        :param start_date: The start date of the historical data range (YYYY-MM-DD).
        :param end_date: The end date of the historical data range (YYYY-MM-DD).
        :param timeframe: The timeframe for the data (e.g., '1D' for daily data).
        :return: Historical closing prices as a list of floats.
        """
        # Fetch historical prices
        historical_data = self.api.get_bars(symbol, timeframe, start=start_date, end=end_date)
        
        # Extract closing prices
        closing_prices = [bar.c for bar in historical_data]
        
        return closing_prices
