import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


tick= yf.Ticker('amzn')
tick_historical = tick.history(start="2021-06-02", end="2022-06-07", interval="1d")

data = yf.download("AMZN NVDA MSFT", start="2023-01-01", end="2023-11-24", group_by='tickers')

tickers_list = ["aapl", "goog", "amzn", "BAC", "BA"] # example list
tickers_data= {} # empty dictionary
for ticker in tickers_list:
    ticker_object = yf.Ticker(ticker)

    #convert info() output from dictionary to dataframe
    temp = pd.DataFrame.from_dict(ticker_object.info, orient="index")
    temp.reset_index(inplace=True)
    temp.columns = ["Attribute", "Recent"]
    
    # add (ticker, dataframe) to main dictionary
    tickers_data[ticker] = temp


# get option chain calls data for specific expiration date
opt = tick.option_chain(date='2023-07-24')
print(opt.calls)