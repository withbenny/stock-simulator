import os
import re
import csv
import math
import json
import requests
from dotenv import load_dotenv
from collections import namedtuple

load_dotenv()

INIT_MONEY = 100_000

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

        # username can only be numbers[0-9] and letters[a-z, A-Z]
        # username cannot start with a number
        # username must be longer than 5
        if not self.isValidName(username):
            raise ValueError("Invalid username.")
        
        # If username is new, creat a new file 
        if not os.path.exists(username + '.csv'):
            with open(username + '.csv', 'w', newline='') as csvfile:
                headers = ['symbol', 'quantity']
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerow({'symbol': username + 'CASH', 'quantity':INIT_MONEY})
        
        # If username is exist, load the data
        else:
            with open(username + '.csv', 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    symbol = row['symbol']
                    quantity = row['quantity']
                    self.holdings[symbol] = quantity
                
                if self.username + 'CASH' in self.holdings:
                    self.cash = self.holdings.get(self.username + 'CASH')
                else:
                    self.cash = INIT_MONEY
                
    def trade(self, symbol:str, mode:str, share:float) -> None:
        self.symbol = symbol
        self.mode = mode
        self.share = share

        cash = self.cash
        
        if share <= 0 or price <= 0:
            raise ValueError("Invalid values.")
        
        # share keeps four decimal places to support fractional shares
        share = math.floor(share * 10000) / 10000

        # BUY
        # Ignore the case of 'buy' and 'sell'
        if mode.casefold() == 'buy':
            price = GetTicker(symbol).latestPrice()
            cost = price * share
            if cash - cost >= 0:
                cash = cash - cost
                self.holdings[self.username + 'CASH'] = cash
                if symbol in self.holdings:
                    self.holdings[symbol] = math.floor((self.holdings.get(symbol) + share) * 10000) / 10000
                else:
                    self.holdings[symbol] = math.floor(share * 10000) / 10000
            else:
                raise ValueError("Invalid action.")

        # SELL    
        elif mode.casefold() == 'sell':
            price = GetTicker(symbol).latestPrice()
            if symbol in self.holdings:
                before = self.holdings.get(symbol)
                if share <= before:
                    income = price * share
                    cash = cash + income
                    self.holdings[self.username + 'CASH'] = cash
                    if share == before:
                        del self.holdings[symbol]
                    else:
                        self.holdings[symbol] = math.floor((before - share) * 10000) / 10000
                else:
                    raise ValueError("Invalid action.")
            else:
                raise ValueError("Invalid action.")
        
        # Other MODE
        else:
            raise ValueError("Invalid trade mode.")
        
        # Save the data
        with open(self.username + '.csv', 'w', newline='') as csvfile:
            headers = ['symbol', 'quantity']
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writerows(self.holdings)
        
        
    def isValidName(self, username:str) -> bool:
        partten = r'^[a-zA-Z][a-zA-Z0-9]*$'
        if re.match(partten, username):
            if len(username) >= 5:
                return True
            else:
                return False
        else:
            return False
    