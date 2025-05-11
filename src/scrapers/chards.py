import requests
from bs4 import BeautifulSoup
import re
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('price_scraper')

coins = {
    "sovereign": ["https://www.chards.co.uk/2025-uk-full-gold-sovereign-coin/2952","Gold Sovereign"],
    "gold_britannia": ["https://www.chards.co.uk/2025-gold-britannia-1-oz-bullion-coin/2984", "Gold Britannia"],
    "silver_britannia": ["https://www.chards.co.uk/2025-silver-britannia-1-oz-bullion-coin/20760", "Silver Britannia"]
}

def update_price(coin):
    url = coins[coin][0]
    coin_name = coins[coin][1]
    price = scrape_chards_price(url, coin_name)
    
    if price:
        logger.info(f"Successfully scraped price: £{price}")
        return price, coin_name
    else:
        logger.error("Failed to scrape price")
        return None


def scrape_chards_price(url, coin_name):
    try:
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.chards.co.uk/'
        }
        
        # Make the request with a timeout
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check if request was successful
        if response.status_code != 200:
            logger.error(f"Request failed with status code: {response.status_code}")
            return None
            
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for price patterns in the HTML
        pound_pattern = re.compile(r'£(\d+[\.,]\d+)')
        
        # Method 1: Try to find all td elements and check for price
        for td in soup.find_all('td'):
            text = td.get_text(strip=True)
            match = pound_pattern.search(text)
            if match:
                price = float(match.group(1).replace(',', '.'))
                logger.info(f"Found {coin_name} price in td element: £{price}")
                # # Filter for likely sovereign prices (around £600-£700)
                # if 500 <= price <= 800:
                return price
        
        # Method 2: If not found, search all text for pound signs and numbers
        all_prices = []
        for element in soup.find_all(text=True):
            matches = pound_pattern.findall(element)
            for match in matches:
                try:
                    price = float(match.replace(',', '.'))
                    all_prices.append(price)
                except ValueError:
                    continue
        
        # Filter prices to find likely prices
        if all_prices:
            logger.info(f"Found prices: {all_prices}")
            coin_prices = [p for p in all_prices if 500 <= p <= 800]
            if coin_prices:
                logger.info(f"Likely {coin_name} price: £{coin_prices[0]}")
                return coin_prices[0]
            else:
                logger.warning(f"No prices in {coin_name} range found. Using first price: £{all_prices[0]}")
                return all_prices[0]
        
        logger.warning("No prices found on page")
        return None
        
    except Exception as e:
        logger.error(f"Error scraping price: {e}")
        return None

# Example usage (only runs if script is executed directly)
if __name__ == "__main__":
    price, coin_name = update_price("sovereign") # Test
    if price:
        print(f"The current {coin_name} price is: £{price}")
    else:
        print("Could not find the price")
    price, coin_name = update_price("gold_britannia") # Test
    if price:
        print(f"The current {coin_name} price is: £{price}")
    else:
        print("Could not find the price")
    price, coin_name = update_price("silver_britannia") # Test
    if price:
        print(f"The current {coin_name} price is: £{price}")
    else:
        print("Could not find the price")