import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import os

# Record the start time of the script
start_time = time.time()

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
        market_cap = stock.info.get('marketCap', 0)
        if market_cap and market_cap > 5e9:
            large_cap_stocks.append(symbol)
            #print(f"Processing symbol {symbol}")
    except Exception as e:
        print(f"Error processing symbol {symbol}: {e}")

# Print the list of large-cap stocks
print("Large-cap stocks (market cap > 5bn):")
#for stock in large_cap_stocks:
#    print(stock)

# Save to a CSV file with current date and time
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = '/var/www/html/pyethone/scripts/stocks/scrap'
#output_file = os.path.join(output_dir, f'large_cap_stocks2_{current_datetime}.csv')
output_file = os.path.join(output_dir, f'large_cap_stocks2.csv')
large_cap_df = pd.DataFrame(large_cap_stocks, columns=['Symbol'])
large_cap_df.to_csv(output_file, index=False)

# Calculate and print the execution time
end_time = time.time()
execution_time = end_time - start_time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Script to get 5bn cap executed in {execution_time:.2f} seconds at {current_time}")
print("------------")
