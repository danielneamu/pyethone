import yfinance as yf
import pandas as pd

def get_stock_symbols(url, column_name):
    tables = pd.read_html(url)
    for table in tables:
        if column_name in table.columns:
            return table[column_name].tolist()
    return []

# URLs for NYSE and NASDAQ stocks
nyse_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
nasdaq_url = 'https://en.wikipedia.org/wiki/NASDAQ-100'

# Get stock symbols
nyse_symbols = get_stock_symbols(nyse_url, 'Symbol')
nasdaq_symbols = get_stock_symbols(nasdaq_url, 'Ticker')

# Combine the symbols
all_symbols = nyse_symbols + nasdaq_symbols

# Filter stocks with market cap > 5bn
large_cap_stocks = []
for symbol in all_symbols:
    try:
        stock = yf.Ticker(symbol)
        market_cap = stock.info['marketCap']
        if market_cap and market_cap > 5e9:
            large_cap_stocks.append(symbol)
            print(f"Processing symbol {symbol}: {e}")
    except Exception as e:
        print(f"Error processing symbol {symbol}: {e}")

# Print or save the list of large-cap stocks
print("Large-cap stocks (market cap > 5bn):")
for stock in large_cap_stocks:
    print(stock)

# Optional: Save to a CSV file
large_cap_df = pd.DataFrame(large_cap_stocks, columns=['Symbol'])
large_cap_df.to_csv('large_cap_stocks.csv', index=False)
