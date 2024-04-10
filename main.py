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
symbol = input("Enter the ticker symbol of the stock you want to analyze: ")
start_date = '2023-01-01'
end_date = '2023-03-31'
historical_prices = alpaca_integration.fetch_historical_prices(symbol, start_date, end_date)

# Calculate SMAs
sma_20 = trading_strategy.calculate_sma(historical_prices, window=20)
sma_50 = trading_strategy.calculate_sma(historical_prices, window=50)
print(f"SMA-20 for {symbol}: {sma_20}")
print(f"SMA-50 for {symbol}: {sma_50}")

# Generate SMA crossover signals
sma_signals = trading_strategy.generate_sma_crossover_signals(sma_20, sma_50)
print("SMA Crossover Signals:")
for i, signal in enumerate(sma_signals):
    print(f"Day {i+1}: {signal}")

# Optional: Use OpenAI for sentiment analysis or additional insights
headline = input("Enter the headline for sentiment analysis: ")
sentiment = openai_integration.analyze_sentiment(headline)
print("Sentiment Analysis Result:", sentiment)
# Further logic to execute trades based on signals and potentially sentiment analysis
