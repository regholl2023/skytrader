import unittest
import numpy as np
from trading_strategy import TradingStrategy

class TestTradingStrategy(unittest.TestCase):
    def setUp(self):
        self.trading_strategy = TradingStrategy()

    def test_calculate_macd(self):
        # Sample historical prices
        prices = [100, 102, 105, 110, 108, 109, 107, 105, 103, 100, 98, 96, 95, 97, 98, 100]
        
        # Expected MACD line, signal line, and MACD histogram
        expected_macd_line = [0, 0.75, 2.71, 6.08, 5.13, 4.55, 2.89, 0.97, -1.05, -3.88, -6.58, -8.93, -10.31, -9.87, -8.66, -6.51]
        expected_signal_line = [0, 0.25, 1.23, 3.06, 4.07, 4.30, 4.04, 3.42, 2.75, 1.45, -0.02, -1.77, -3.70, -5.73, -7.40, -8.32]
        expected_macd_histogram = [0, 0.50, 1.48, 3.02, 1.06, 0.25, -1.15, -2.45, -3.80, -5.33, -6.56, -7.16, -6.61, -4.14, -1.26, 1.81]

        # Calculate MACD
        macd_line, signal_line, macd_histogram = self.trading_strategy.calculate_macd(prices)

        # Assert the correctness of the calculated MACD values
        np.testing.assert_allclose(macd_line, expected_macd_line, rtol=1e-2)
        np.testing.assert_allclose(signal_line, expected_signal_line, rtol=1e-2)
        np.testing.assert_allclose(macd_histogram, expected_macd_histogram, rtol=1e-2)

if __name__ == '__main__':
    unittest.main()
