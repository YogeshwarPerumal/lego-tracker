import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PriceTracker:
    def __init__(self, products_file='products.json'):
        self.products_file = products_file
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def load_products(self):
        try:
            with open(self.products_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading products: {e}")
            return []
    
    def save_products(self, products):
        try:
            with open(self.products_file, 'w') as f:
                json.dump(products, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving products: {e}")
    
    def get_price(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            scripts = soup.find_all("script")

            for script in scripts:
                if script.string and "price" in script.string:
                    # Try to find JSON-like data
                    match = re.search(r'"price":\s*"?(₹?[\d,]+)"?', script.string)
                    print("match - ", match)
                    if match:
                        price_text = match.group(1).replace("₹", "").replace(",", "")
                        return int(price_text)
            return None
        except Exception as e:
            logging.error(f"Error fetching price: {e}")
            return None
    
    def check_prices(self):
        products = self.load_products()
        price_drops = []
        
        for product in products:
            current_price = self.get_price(product['url'])
            if current_price:
                product['current_price'] = current_price
                product['last_checked'] = datetime.now().isoformat()
                
                if current_price <= product['threshold_price']:
                    price_drops.append({
                        'name': product['name'],
                        'url': product['url'],
                        'current_price': current_price,
                        'threshold_price': product['threshold_price']
                    })
                    logging.info(f"Price drop alert for {product['name']}: ₹{current_price}")
        
        self.save_products(products)
        return price_drops