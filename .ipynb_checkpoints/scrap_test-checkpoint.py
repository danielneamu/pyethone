import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=ASML&apikey=FVQT5WXFOHY2UX43'
r = requests.get(url)
data = r.json()

print(data)