import os
from alpaca_integration import AlpacaIntegration
from trading_strategy import TradingStrategy
from openai_integration import OpenAIIntegration

print("Starting SkyTrade.")

# Initialize
alpaca_integration = AlpacaIntegration()
trading_strategy = TradingStrategy()
openai_integration = OpenAIIntegration()

# Fetch historical prices for a symbol
symbol = 'AAPL'
start_date = '2023-01-01'
end_date = '2023-03-31'
historical_prices = alpaca_integration.fetch_historical_prices(symbol, start_date, end_date)

# Calculate SMA
sma_20 = trading_strategy.calculate_sma(historical_prices, window=20)
print(f"SMA-20 for {symbol}: {sma_20}")

# Generate Trading Signals
signals = trading_strategy.generate_signals(historical_prices, sma_window=20)

# Optional: Use OpenAI for sentiment analysis or additional insights
sentiment = openai_integration.analyze_sentiment("AAPL stock news headline here")
print("Sentiment Analysis Result:", sentiment)
# Further logic to execute trades based on signals and potentially sentiment analysis