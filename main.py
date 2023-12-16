import stock

# sim = stock.Simulate('test1').trade('AAPL', 'buy', 10)
price, time = stock.GetTicker('AAPL').previousClosePrice()
print(time)

api_url = 'https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-charts'
api_key = 'c2d0e0f0aamshb6b5b0b3b5b0c2fp1e3e4ajsnb9b6b5b0b3b5'
stock.SetAPI(api_url,api_key)

stock.GetTicker('AAPL').latestData()