import os
import json
import requests
from dotenv import load_dotenv
from collections import namedtuple

load_dotenv()

class Price(namedtuple('Price', 'price currency')):
    pass

class GetTicker:
    def __init__(self, ticker:list) -> None:
        self.ticker = ticker
        
    def latestData(self) -> dict:
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
        price = data['quoteResponse']['result'][0]['regularMarketPrice']
        
        return price
    
    def latestPriceWithCurrency(self) -> Price:
        data = self.latestData()
        price = data['quoteResponse']['result'][0]['regularMarketPrice']
        currency = data['quoteResponse']['result'][0]['currency']
        
        return Price(price, currency)
    
    