import os
from dotenv import load_dotenv
import requests

load_dotenv()

def get_price(symbol):
    # Define the API endpoint with the symbol provided as an argument
    api_key = os.getenv('API_KEY')
    url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}?apikey={api_key}"
    # Make a request to the endpoint
    response = requests.get(url)
    # Parse the response to JSON
    data = response.json()
    # If data is not empty and 'price' is in the first dictionary of the list, return the price
    if data and 'price' in data[0]: 
        return data[0]['price']
    else:
        # Raise an exception if we couldn't get the stock price
        raise Exception("Unable to fetch stock price")
