import os
from alpaca_trade_api.rest import REST
from alpaca_trade_api.rest import APIError  # Import APIError for catching Alpaca API specific errors
from dotenv import load_dotenv

load_dotenv()  # This loads the .env file at the project root

class AlpacaIntegration:
    def __init__(self):
        self.api = REST(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), base_url='https://paper-api.alpaca.markets')
    
    def get_account_info(self):
        return self.api.get_account()

    def fetch_market_data(self, symbol, timeframe='1D', limit=100):
        bars = self.api.get_bars(symbol, timeframe, limit=limit)
        return bars

    def fetch_historical_prices(self, symbol, start_date, end_date, timeframe='1D'):
        """
        Fetch historical price data for a given symbol within a specified date range.
        Includes error handling to manage exceptions and ensure data integrity.

        :param symbol: The symbol to fetch data for.
        :param start_date: The start date of the historical data range (YYYY-MM-DD).
        :param end_date: The end date of the historical data range (YYYY-MM-DD).
        :param timeframe: The timeframe for the data (e.g., '1D' for daily data).
        :return: Historical closing prices as a list of floats, or None if an error occurs.
        """
        try:
            # Fetch historical prices
            historical_data = self.api.get_bars(symbol, timeframe, start=start_date, end=end_date)
            
            # Extract closing prices
            closing_prices = [bar.c for bar in historical_data]
            
            # Verify that closing_prices is not empty
            if not closing_prices:
                print(f"No data returned for {symbol} from {start_date} to {end_date}.")
                return None
            
            return closing_prices
        except APIError as e:
            print(f"An error occurred while fetching historical data for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

