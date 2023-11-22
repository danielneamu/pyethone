import sys
import json
import yfinance as yf
import pandas_ta as ta
from datetime import datetime, timedelta

# needed for graphs section
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import os  # Import the os module

# Redirect stdout to stderr
sys.stdout = sys.stderr

# Debugging: Print a message when the script starts
print("Script started", file=sys.stderr)

# Define the stock symbol  from command-line arguments
# symbol = 'AMZN'
symbol = sys.argv[1] if len(sys.argv) > 1 else 'DEFAULT_SYMBOL'

# Define the timeframe
end_date = datetime.today()
start_date = end_date - timedelta(days=120)

# Debugging: Print a message before fetching stock data
print("Fetching stock data", file=sys.stderr)

# Fetch stock data using yfinance
try:
    stock_data = yf.download(symbol, start=start_date, end=end_date)
except Exception as e:
    print(f"Error fetching stock data: {e}", file=sys.stderr)
    sys.exit(1)

# Calculate technical indicators using pandas-ta
stock_data.ta.macd(append=True)
stock_data.ta.rsi(append=True)
stock_data.ta.bbands(append=True)
stock_data.ta.obv(append=True)

# Calculate additional technical indicators
stock_data.ta.sma(length=20, append=True)
stock_data.ta.ema(length=50, append=True)
stock_data.ta.stoch(append=True)
stock_data.ta.adx(append=True)

# Calculate other indicators
stock_data.ta.willr(append=True)
stock_data.ta.cmf(append=True)
stock_data.ta.psar(append=True)

# Convert OBV to million
stock_data['OBV_in_million'] = stock_data['OBV'] / 1e7
stock_data['MACD_histogram_12_26_9'] = stock_data['MACDh_12_26_9']

# Summarize technical indicators for the last day
last_day_summary = {
    'symbol': symbol,
    'Adj_Close': float(stock_data.iloc[-1]['Adj Close']),
    'MACD_12_26_9': float(stock_data.iloc[-1]['MACD_12_26_9']),
    'MACD_histogram_12_26_9': float(stock_data.iloc[-1]['MACD_histogram_12_26_9']),
    'RSI_14': float(stock_data.iloc[-1]['RSI_14']),
    'BBL_5_2.0': float(stock_data.iloc[-1]['BBL_5_2.0']),
    'BBM_5_2.0': float(stock_data.iloc[-1]['BBM_5_2.0']),
    'BBU_5_2.0': float(stock_data.iloc[-1]['BBU_5_2.0']),
    'SMA_20': float(stock_data.iloc[-1]['SMA_20']),
    'EMA_50': float(stock_data.iloc[-1]['EMA_50']),
    'OBV_in_million': float(stock_data.iloc[-1]['OBV_in_million']),
    'STOCHk_14_3_3': float(stock_data.iloc[-1]['STOCHk_14_3_3']),
    'STOCHd_14_3_3': float(stock_data.iloc[-1]['STOCHd_14_3_3']),
    'ADX_14': float(stock_data.iloc[-1]['ADX_14']),
    'WILLR_14': float(stock_data.iloc[-1]['WILLR_14']),
    'CMF_20': float(stock_data.iloc[-1]['CMF_20']),
    'PSARl_0.02_0.2': float(stock_data.iloc[-1]['PSARl_0.02_0.2']),
    'PSARs_0.02_0.2': float(stock_data.iloc[-1]['PSARs_0.02_0.2'])
}

# Convert the dictionary to a JSON-formatted string
json_output = json.dumps(last_day_summary)

# Summarize technical indicators for the last day
day_summary = stock_data.iloc[-1][['Adj Close',
    'MACD_12_26_9','MACD_histogram_12_26_9', 'RSI_14', 'BBL_5_2.0', 'BBM_5_2.0', 'BBU_5_2.0','SMA_20', 'EMA_50','OBV_in_million', 'STOCHk_14_3_3', 
    'STOCHd_14_3_3', 'ADX_14',  'WILLR_14', 'CMF_20', 
    'PSARl_0.02_0.2', 'PSARs_0.02_0.2'
]]
print("Summary of Technical Indicators for the Last Day:")
print("Working on the new prompt!!!")
## Work on the prompt
new_prompt = """
Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
a modern counterpart to Charles Dow, John Bollinger, and Alan Andrews. \
Your mastery encompasses both stock fundamentals and intricate technical indicators. \
You possess the ability to decode complex market dynamics, \
providing clear insights and recommendations backed by a thorough understanding of interrelated factors. \
Your expertise extends to practical tools like the pandas_ta module, \
allowing you to navigate data intricacies with ease. \
As a TA authority, your role is to decipher market trends, make informed predictions, and offer valuable perspectives.

given {} TA data as below on the last trading day, what will be the next few days possible stock price movement? 

Summary of Technical Indicators for the Last Day:
{}""".format(symbol,day_summary)

last_day_summary['new_prompt'] = new_prompt

print(new_prompt)


##############################################################
# PLOTTING section
##############################################################

# Plot the technical indicators
plt.figure(figsize=(11, 7))

# Price Trend Chart
plt.subplot(3, 3, 1)
plt.plot(stock_data.index, stock_data['Adj Close'], label='Adj Close', color='blue')
plt.plot(stock_data.index, stock_data['EMA_50'], label='EMA 50', color='green')
plt.plot(stock_data.index, stock_data['SMA_20'], label='SMA_20', color='orange')
plt.title("Price Trend")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))  # Format date as "Jun14"
plt.xticks(rotation=45, fontsize=8)  # Adjust font size
plt.legend()

# On-Balance Volume Chart
plt.subplot(3, 3, 2)
plt.plot(stock_data['OBV'], label='On-Balance Volume')
plt.title('On-Balance Volume (OBV) Indicator')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))  # Format date as "Jun14"
plt.xticks(rotation=45, fontsize=8)  # Adjust font size
plt.legend()

# MACD Plot
plt.subplot(3, 3, 3)
plt.plot(stock_data['MACD_12_26_9'], label='MACD')
plt.plot(stock_data['MACDh_12_26_9'], label='MACD Histogram')
plt.title('MACD Indicator')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))  # Format date as "Jun14"
plt.xticks(rotation=45, fontsize=8)  # Adjust font size
plt.title("MACD")
plt.legend()

# RSI Plot
plt.subplot(3, 3, 4)
plt.plot(stock_data['RSI_14'], label='RSI')
plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
plt.legend()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))  # Format date as "Jun14"
plt.xticks(rotation=45, fontsize=8)  # Adjust font size
plt.title('RSI Indicator')

# Bollinger Bands Plot
plt.subplot(3, 3, 5)
plt.plot(stock_data.index, stock_data['BBU_5_2.0'], label='Upper BB')
plt.plot(stock_data.index, stock_data['BBM_5_2.0'], label='Middle BB')
plt.plot(stock_data.index, stock_data['BBL_5_2.0'], label='Lower BB')
plt.plot(stock_data.index, stock_data['Adj Close'], label='Adj Close', color='brown')
plt.title("Bollinger Bands")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))  # Format date as "Jun14"
plt.xticks(rotation=45, fontsize=8)  # Adjust font size
plt.legend()

# Stochastic Oscillator Plot
plt.subplot(3, 3, 6)
plt.plot(stock_data.index, stock_data['STOCHk_14_3_3'], label='Stoch %K')
plt.plot(stock_data.index, stock_data['STOCHd_14_3_3'], label='Stoch %D')
plt.title("Stochastic Oscillator")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))  # Format date as "Jun14"
plt.xticks(rotation=45, fontsize=8)  # Adjust font size
plt.legend()

# Williams %R Plot
plt.subplot(3, 3, 7)
plt.plot(stock_data.index, stock_data['WILLR_14'])
plt.title("Williams %R")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))  # Format date as "Jun14"
plt.xticks(rotation=45, fontsize=8)  # Adjust font size

# ADX Plot
plt.subplot(3, 3, 8)
plt.plot(stock_data.index, stock_data['ADX_14'])
plt.title("Average Directional Index (ADX)")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))  # Format date as "Jun14"
plt.xticks(rotation=45, fontsize=8)  # Adjust font size

# CMF Plot
plt.subplot(3, 3, 9)
plt.plot(stock_data.index, stock_data['CMF_20'])
plt.title("Chaikin Money Flow (CMF)")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b%d'))  # Format date as "Jun14"
plt.xticks(rotation=45, fontsize=8)  # Adjust font size

# Debugging: Print a message before saving plots
print("Saving plots", file=sys.stderr)

# Save the plots as images
plot_images_dir = "/var/www/html/pyethone/scripts/ta/images"  # Change this to the actual path
#os.makedirs(plot_images_dir, exist_ok=True)  # Ensure the directory exists

plot_paths = []  # Store the paths of saved plots

# Generate chart img file
plot_filename = f"{symbol}.png"
plot_path = os.path.join(plot_images_dir, plot_filename)
plt.subplot(3, 3, 1)
plt.tight_layout()

# Save the plot
try:
    plt.savefig(plot_path)
    plot_paths.append(plot_path)
except FileNotFoundError as e:
    print(f"Error saving plot: {e}")


# Close the figure to avoid displaying the plots in the terminal
plt.close()

# Include the image paths in the JSON response
last_day_summary['plot_paths'] = plot_paths


# Convert the dictionary to a JSON-formatted string
json_output = json.dumps(last_day_summary)

# Print the JSON-formatted string
# Print the JSON-formatted string to stderr
print(json_output, file=sys.stderr)

# Show the plots
# plt.tight_layout()
# plt.show()