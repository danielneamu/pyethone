import yfinance as yf

# Example: Fetch Apple's stock data
ticker = "AAPL"
data = yf.download(ticker, start="2021-01-01", end="2021-12-31")

print(data.head())
