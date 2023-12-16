import csv
import datetime
import json
import math
import os
import re
import time
from collections import namedtuple
from typing import Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

INIT_MONEY = 100_000

class SetAPI:
    def __init__(self, api_url:str, api_key:str) -> None:
        self.api_url = api_url
        self.api_key = api_key

    def getAPI(self) -> Tuple[str, str]:
        api_url = self.api_url
        api_key = self.api_key
        return api_url, api_key

class GetTicker:
    def __init__(self, ticker:str) -> None:
        self.ticker = ticker
        
    def latestData(self) -> dict:
        # Get api_key in YH Finances
        # api_key is in .env file, create it if not have one
        api_url, api_key = SetAPI().getAPI()
        symbol = {'symbols': self.ticker}
        
        headers = {
            'x-api-key': api_key
        }
        
        response = requests.get(api_url, headers=headers, params=symbol, timeout=(3,7))
        # data now is a dict
        data = json.loads(response.content)

        return data
    
    def loadData(self, json_file:str) -> dict:
        # Load the data from a json file
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        return data

    def saveData(self, data:dict, json_file:str) -> None:
        # Save the dictionary data into a json file
        with open(json_file, 'w') as f:
            json.dump(data, f)

    def getTime(self, data:dict) -> datetime.datetime:
        # regularMarketTime is the time of the stock
        time = data['quoteResponse']['result'][0]['regularMarketTime']
        time = datetime.datetime.fromtimestamp(time)

        return time

    def getCurrency(self, data:dict) -> str:
        # currency is the currency of the stock
        currency = data['quoteResponse']['result'][0]['currency']
        
        return currency

    def getState(self, data:dict) -> str:
        # state is the state of the stock
        state = data['quoteResponse']['result'][0]['state']
        
        return state

    def latestPrice(self, data:dict) -> Tuple[float, datetime.datetime, str]:
        # regularMarketPrcie is the current price of the stock
        price = data['quoteResponse']['result'][0]['regularMarketPrice']
        
        time = self.getTime(data)
        currency = self.getCurrency()

        return price, time, currency

    def previousClosePrice(self, data:dict) -> Tuple[float, datetime.datetime]:
        # regularMarketPreviousClose is the previous close price of the stock
        price = data['quoteResponse']['result'][0]['regularMarketPreviousClose']

        time = self.getTime(data)
        # The close date is the day before the current date
        close_date = (time - datetime.timedelta(days=1)).date()
        
        return price, close_date
    
    def openPrice(self, data:dict) -> Tuple[float, datetime.datetime]:
        # regularMarketOpen is the open price of the stock
        price = data['quoteResponse']['result'][0]['regularMarketOpen']
        
        date = self.getTime(data).date()

        return price, date

    def closePrice(self, data:dict) -> Tuple[float, datetime.datetime]:
        # If the market is closed, return the latest price
        if self.getState() == 'CLOSED':
            price, date = self.latestPrice(data)[0, 1]
        # If the market is open, return the previous close price
        else:
            price, date = self.previousClosePrice(data)

        return price, date
    
    def highPrice(self, data:dict) -> Tuple[float, datetime.datetime]:
        # regularMarketDayHigh is the high price of the stock
        price = data['quoteResponse']['result'][0]['regularMarketDayHigh']

        date = self.getTime(data).date()

        return price, date

    def lowPrice(self, data:dict) -> Tuple[float, datetime.datetime]:
        # regularMarketDayLow is the low price of the stock
        price = data['quoteResponse']['result'][0]['regularMarketDayLow']

        date = self.getTime().date()

        return price, date

    def volume(self, data:dict, range:str) -> float:
        # regularMarketVolume is the volume of the stock
        if range == 'TODAY' or range == None:
            volume = data['quoteResponse']['result'][0]['regularMarketVolume']
        elif range == '10DAY':
            volume = data['quoteResponse']['result'][0]['averageDailyVolume10Day']
        elif range == '3MONTH':
            volume = data['quoteResponse']['result'][0]['averageDailyVolume3Month']
        else:
            raise ValueError("Invalid range.")
        return volume

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
                    with open(username + '.csv', 'w', newline='') as csvfile:
                        headers = ['symbol', 'quantity']
                        writer = csv.DictWriter(csvfile, fieldnames=headers)
                        writer.writeheader()
                        writer.writerow({'symbol': username + 'CASH', 'quantity':self.cash})
        print(str(self.holdings))

    def isValidName(self, username:str) -> bool:
        partten = r'^[a-zA-Z][a-zA-Z0-9]*$'
        if re.match(partten, username):
            if len(username) >= 5:
                return True
            else:
                return False
        else:
            return False

    def currentCash(self) -> float:
        return self.cash

    def trade(self, symbol:str, mode:str, share:float) -> None:
        if share <= 0:
            raise ValueError("Invalid values.")

        self.cash = self.holdings.get(self.username + 'CASH')
        cash = self.cash
        cash = float(cash)
        
        # share keeps four decimal places to support fractional shares
        share = math.floor(share * 10000) / 10000
        
        # BUY
        # Ignore the case of 'buy' and 'sell'
        if mode.casefold() == 'buy':
            price = GetTicker(symbol).latestPrice()
            cost = price * share
            if cash - cost >= 0:
                cash = cash - cost
                # Chaneg the current cash
                self.holdings[self.username + 'CASH'] = cash

                if symbol in self.holdings:
                    self.holdings[symbol] = math.floor((float(self.holdings.get(symbol)) + share) * 10000) / 10000
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
                    # Change the current cash
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
        
        print(str(self.holdings))
        self.saveData()

    def saveData(self) -> None:
        # Save the data
        with open(self.username + '.csv', 'w', newline='') as csvfile:
            headers = ['symbol', 'quantity']
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            # Save the cash
            writer.writerow({'symbol': self.username + 'CASH', 'quantity': self.holdings[self.username + 'CASH']})
            # Save the holdings
            for stock_symbol, quantity in self.holdings.items():
                if stock_symbol != self.username + 'CASH':
                    writer.writerow({'symbol': stock_symbol, 'quantity': quantity})
