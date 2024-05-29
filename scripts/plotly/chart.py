import plotly.express as px
import yfinance as yf
import pandas as pd

msft = yf.Ticker("MSFT")

# get all stock info
poza=msft.history(period="3y")

tickers = yf.Tickers('msft aapl goog')

# access each ticker using (example)
#print(tickers.tickers['MSFT'].info)
#print(tickers.tickers['AAPL'].history(period="1mo"))
#print(tickers.tickers['GOOG'].actions)

print(poza)

# Create a line chart using Plotly Express
fig = px.line(poza, x=poza.index, y="Close", title="Google Stock Prices Over tiiiiiiime")

# Show the figure
#fig.show()

# Save the figure as an HTML file
try:
    fig.write_html("/var/www/html/pyethone/scripts/plotly/plot.html")
    print("Plot generation successful.")
except Exception as e:
    print(f"Error writing HTML file: {e}")

print("Plot generation successful.")




df = px.data.stocks(indexed=True)-1
print(df)
fig = px.area(df, facet_col="company", facet_col_wrap=2)
#fig.show()

