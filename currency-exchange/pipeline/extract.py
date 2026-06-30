import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_currency_data(date_str):
    """Fetches exchange rates from Frankfurter API with USD as base."""
    # If it is a weekend, the API will naturally return the closest previous Friday
    url = f"https://api.frankfurter.dev/v1/{date_str}"
    params = {
        "base": "USD",
        "symbols": "UZS,RUB,EUR,GBP"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch data for {date_str}: Status {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Network error on {date_str}: {e}")
        return None
