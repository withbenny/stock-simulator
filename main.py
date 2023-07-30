import stock

apple = stock.GetTicker('AAPL')

data = apple.latestData()
price = apple.latestPriceWithCurrency()

print(price.price, price.currency)