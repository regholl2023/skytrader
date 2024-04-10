from .alpaca_integration import AlpacaIntegration
from .openai_integration import OpenAIIntegration

class TradingBot:
    def __init__(self):
        self.alpaca = AlpacaIntegration()
        self.openai = OpenAIIntegration()
    
    # Implement your trading logic here
