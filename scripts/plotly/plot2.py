import yfinance as yf
import pandas as pd
import plotly.express as px

# Replace the ticker symbols with your desired list of symbols
ticker_symbols = ['AMZN',  'MSFT',  'THC', 'HCA', 'CVX', 'LEU', 'SGML','LIN', 'KO','CVS','MA']

# Create an empty DataFrame to store the data
df_yfinance = pd.DataFrame()

# Download historical data for each ticker symbol with a weekly interval
for ticker in ticker_symbols:
    stock_data = yf.download(ticker, start='2023-11-20', end='2023-11-23', interval='1d')  # Adjust the start and end dates as needed
    df_yfinance[ticker] = stock_data['Close']

# Reset index to make 'Date' a regular column
df_yfinance.reset_index(inplace=True)

# Melt the DataFrame
df_melted = pd.melt(df_yfinance, id_vars=['Date'], var_name='Ticker', value_name='Value')
df_melted['Percentage_Change'] = (df_melted['Value'] / df_melted.groupby('Ticker')['Value'].transform('first') - 1) * 100

# Define a color map for each ticker symbol
color_map = {'AAPL': 'blue', 'GOOG': 'green', 'AMZN': 'red', 'MSFT': 'cyan', 'NFLX': 'orange', 'NVDA': 'purple'}

# Plot using Plotly Express
fig = px.area(df_melted, x='Date', y='Percentage_Change', facet_col="Ticker", facet_col_wrap=2,
              labels={'Percentage_Change': 'Percentage Change from Start'},
              color='Ticker', color_discrete_map=color_map)

print(df_melted)
# Show the figure
fig.show()
