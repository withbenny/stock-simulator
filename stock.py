import os
import re
import csv
import math
import json
import requests
from dotenv import load_dotenv
from collections import namedtuple

load_dotenv()

class Price(namedtuple('Price', 'price currency')):
    pass

class GetTicker:
    def __init__(self, ticker:str) -> None:
        self.ticker = ticker
        
    def latestData(self) -> dict:
        # Get api_key in YH Finance
        # api_key is in .env file, create it if not have one
        api_key = os.getenv('YH_FINANCE_KEY')
        api_url = "https://yfapi.net/v6/finance/quote"
        symbol = {'symbols': self.ticker}
        
        headers = {
            'x-api-key': api_key
        }
        
        response = requests.get(api_url, headers=headers, params=symbol, timeout=(3,7))
        # data now is a dict
        data = json.loads(response.content)
        
        return data
    
    def latestPrice(self) -> float:
        data = self.latestData()
        # regularMarketPrcie is the current price of the stock
        price = data['quoteResponse']['result'][0]['regularMarketPrice']
        
        return price
    
    def latestPriceWithCurrency(self) -> Price:
        data = self.latestData()
        price = data['quoteResponse']['result'][0]['regularMarketPrice']
        # currency is USD, TWD...
        currency = data['quoteResponse']['result'][0]['currency']
        
        return Price(price, currency)

class Simulate:
    # Data is stored in username.csv
    def __init__(self, username:str) -> None:
        self.username = username
        self.holdings = {}
        # Init cash of user is 100,000
        self.cash = 100_000

        # username can only be numbers[0-9] and letters[a-z, A-Z]
        # username cannot start with a number
        # username must be longer than 5
        if not self.isValidName(username):
            raise ValueError("Invaild username.")
        
        # If username is new, creat a new file 
        if not os.path.exists(username + '.csv'):
            with open(username + '.csv', 'w', newline='') as csvfile:
                headers = ['symbol', 'quantity']
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerow({'symbol': username+'CASH', 'quantity':self.cash})
        
        # If username is exist, load the data
        else:
            with open(username + '.csv', 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Find the cash of user
                    if row['symbol'] == username + 'CASH':
                        self.cash = row['quantity']
                    symbol = row['symbol']
                    quantity = row['quantity']
                    self.holdings[symbol] = quantity
                
    def trade(self, symbol:str, mode:str, share:float, price:float):
        self.symbol = symbol
        self.mode = mode
        self.share = share
        self.price = price
        
        if share <= 0 or price <= 0:
            raise ValueError("The number of shares and price must be positive.")
        
        # share keeps four decimal places to support fractional shares
        share = math.floor(share * 10000) / 10000
        price = math.floor(price * 100) / 100

        if mode.casefold() == 'buy':
            pass
            
        elif mode.casefold() == 'sell':
            pass
            
        else:
            raise ValueError("Invalid trade mode. Please use buy or sell.(Not case sensitive)")
        
        
    def isValidName(self, username:str) -> bool:
        partten = r'^[a-zA-Z][a-zA-Z0-9]*$'
        if re.match(partten, username):
            if len(username) >= 5:
                return True
            else:
                return False
        else:
            return False
    