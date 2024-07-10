import sys
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class StockAnalyzer:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = None

        # Configuration for various indicators
        self.indicators_config = {
            'short_window': 50,
            'long_window': 200,
            'rsi_window': 14,
            'bollinger_window': 20,
            'atr_window': 14,
            'macd_short_window': 12,
            'macd_long_window': 26,
            'macd_signal_window': 9,
            'stoch_k_period': 14,
            'stoch_d_period': 3
        }

    def fetch_data(self):
        """Fetch historical stock data from Yahoo Finance."""
        try:
            self.data = yf.download(
                self.ticker, start=self.start_date, end=self.end_date)
            print(f"Fetched historical data for {self.ticker}")
        except Exception as e:
            print(f"Error fetching data: {e}")

    def calculate_indicators(self):
        """Calculate all necessary indicators."""
        if self.data is None:
            print("No data to analyze. Fetch data first.")
            return

        self.calculate_moving_averages()
        self.calculate_rsi()
        self.calculate_bollinger_bands()
        self.calculate_atr()
        self.calculate_macd()
        self.calculate_stochastic_oscillator()

    def calculate_moving_averages(self):
        """Calculate short and long moving averages."""
        self.data['Short_MA'] = self.data['Close'].rolling(
            window=self.indicators_config['short_window'], min_periods=1).mean()
        self.data['Long_MA'] = self.data['Close'].rolling(
            window=self.indicators_config['long_window'], min_periods=1).mean()

    def calculate_rsi(self):
        """Calculate Relative Strength Index (RSI)."""
        delta = self.data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(
            window=self.indicators_config['rsi_window']).mean()
        loss = - \
            delta.where(delta < 0, 0).rolling(
                window=self.indicators_config['rsi_window']).mean()
        RS = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + RS))

    def calculate_bollinger_bands(self):
        """Calculate Bollinger Bands."""
        rolling_mean = self.data['Close'].rolling(
            window=self.indicators_config['bollinger_window']).mean()
        rolling_std = self.data['Close'].rolling(
            window=self.indicators_config['bollinger_window']).std()
        self.data['Upper_Band'] = rolling_mean + 2 * rolling_std
        self.data['Lower_Band'] = rolling_mean - 2 * rolling_std

    def calculate_atr(self):
        """Calculate Average True Range (ATR)."""
        high_low = self.data['High'] - self.data['Low']
        high_close_prev = (self.data['High'] -
                           self.data['Close'].shift()).abs()
        low_close_prev = (self.data['Low'] - self.data['Close'].shift()).abs()
        true_range = pd.concat(
            [high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        self.data['ATR'] = true_range.rolling(
            window=self.indicators_config['atr_window']).mean()

    def calculate_macd(self):
        """Calculate Moving Average Convergence Divergence (MACD)."""
        exp1 = self.data['Close'].ewm(
            span=self.indicators_config['macd_short_window'], adjust=False).mean()
        exp2 = self.data['Close'].ewm(
            span=self.indicators_config['macd_long_window'], adjust=False).mean()
        self.data['MACD'] = exp1 - exp2
        self.data['MACD Signal'] = self.data['MACD'].ewm(
            span=self.indicators_config['macd_signal_window'], adjust=False).mean()
        self.data['MACD Histogram'] = self.data['MACD'] - \
            self.data['MACD Signal']

    def calculate_stochastic_oscillator(self):
        """Calculate Stochastic Oscillator."""
        min_low = self.data['Low'].rolling(
            window=self.indicators_config['stoch_k_period']).min()
        max_high = self.data['High'].rolling(
            window=self.indicators_config['stoch_k_period']).max()
        self.data['Stoch_K'] = 100 * \
            (self.data['Close'] - min_low) / (max_high - min_low)
        self.data['Stoch_D'] = self.data['Stoch_K'].rolling(
            window=self.indicators_config['stoch_d_period']).mean()

    def plot_analysis(self):
        """Plot stock price and various technical indicators."""
        if self.data is None:
            print("No data to plot. Fetch data and analyze first.")
            return

        plt.figure(figsize=(14, 20))

        # Plot stock price and moving averages
        plt.subplot(7, 1, 1)
        plt.plot(self.data['Close'], label='Stock Price', linewidth=2)
        plt.plot(self.data['Short_MA'], label=f'Short MA ({
                 self.indicators_config["short_window"]} days)', linestyle='--')
        plt.plot(self.data['Long_MA'], label=f'Long MA ({
                 self.indicators_config["long_window"]} days)', linestyle='--')
        plt.title(f'{self.ticker} Stock Price and Moving Averages')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)

        # Plot RSI
        plt.subplot(7, 1, 2)
        plt.plot(self.data['RSI'], label='RSI', color='purple')
        plt.axhline(y=70, color='r', linestyle='--')
        plt.axhline(y=30, color='g', linestyle='--')
        plt.title('Relative Strength Index (RSI)')
        plt.xlabel('Date')
        plt.ylabel('RSI')
        plt.legend()
        plt.grid(True)

        # Plot Bollinger Bands
        plt.subplot(7, 1, 3)
        plt.plot(self.data['Close'], label='Stock Price', linewidth=2)
        plt.plot(self.data['Upper_Band'],
                 label='Upper Bollinger Band', linestyle='--')
        plt.plot(self.data['Lower_Band'],
                 label='Lower Bollinger Band', linestyle='--')
        plt.title('Bollinger Bands')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)

        # Plot MACD
        plt.subplot(7, 1, 4)
        plt.plot(self.data['MACD'], label='MACD', color='blue')
        plt.plot(self.data['MACD Signal'],
                 label='MACD Signal', color='red', linestyle='--')
        plt.bar(self.data.index,
                self.data['MACD Histogram'], label='MACD Histogram', color='gray')
        plt.title('Moving Average Convergence Divergence (MACD)')
        plt.xlabel('Date')
        plt.ylabel('MACD')
        plt.legend()
        plt.grid(True)

        # Plot Stochastic Oscillator
        plt.subplot(7, 1, 5)
        plt.plot(self.data['Stoch_K'], label='Stoch %K', color='purple')
        plt.plot(self.data['Stoch_D'], label='Stoch %D', color='orange')
        plt.axhline(y=80, color='r', linestyle='--')
        plt.axhline(y=20, color='g', linestyle='--')
        plt.title('Stochastic Oscillator')
        plt.xlabel('Date')
        plt.ylabel('Stochastic')
        plt.legend()
        plt.grid(True)

        # Plot ATR with stock price
        plt.subplot(7, 1, 6)
        plt.plot(self.data['Close'], label='Stock Price', linewidth=2)
        plt.twinx()
        plt.plot(self.data['ATR'], label='ATR', color='orange')
        plt.title('Average True Range (ATR) with Stock Price')
        plt.xlabel('Date')
        plt.ylabel('Price / ATR')
        plt.legend(loc='upper left')
        plt.grid(True)

        plt.tight_layout()

        # Save plot as PNG file
        plot_path = '/var/www/html/pyethone/scripts/stocks/ta2/stock_analysis.png'
        plt.savefig(plot_path)
        print(f"Plot saved as '{plot_path}'")

        plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <ticker> <start_date> <end_date>")
        sys.exit(1)

    ticker = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    analyzer = StockAnalyzer(ticker, start_date, end_date)
    analyzer.fetch_data()
    analyzer.calculate_indicators()
    analyzer.plot_analysis()
