import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
# url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=ASML&apikey=FVQT5WXFOHY2UX43'

url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=MSFT&time_from=20231110T0000&time_to=20231119T2359&apikey=H7BPC1RWPLQGRRO5'
r = requests.get(url)
data = r.json()

print(data)