"""
Chards website scraper for precious metals prices
"""
import requests
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger('price_scraper')

# Dictionary of coins with their URLs, names, and price column index
COINS = {
    "sovereign": ["https://www.chards.co.uk/2025-uk-full-gold-sovereign-coin/2952", "Gold Sovereign", 2],
    "gold_britannia": ["https://www.chards.co.uk/2025-gold-britannia-1-oz-bullion-coin/2984", "Gold Britannia", 2],
    "silver_britannia": ["https://www.chards.co.uk/2025-silver-britannia-1-oz-bullion-coin/20760", "Silver Britannia", 3]
}

def get_all_prices():
    """Fetch prices for all coins from Chards"""
    results = {}
    for coin_id in COINS:
        price, coin_name = update_price(coin_id)
        if price:
            results[coin_id] = {
                "price": price,
                "name": coin_name
            }
    return results

def update_price(coin_id):
    """Fetch the price for a specific coin"""
    if coin_id not in COINS:
        logger.error(f"Unknown coin ID: {coin_id}")
        return None, None
        
    url = COINS[coin_id][0]
    coin_name = COINS[coin_id][1]
    price_column = COINS[coin_id][2]
    
    price = scrape_chards_price(url, coin_name, price_column)
    
    if price:
        logger.info(f"Successfully scraped {coin_name} price: £{price}")
        return price, coin_name
    else:
        logger.error(f"Failed to scrape {coin_name} price")
        return None, coin_name

def scrape_chards_price(url, coin_name, price_column):
    """Scrape the price from a Chards product page"""
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
        
        # Try to extract price from the table
        price = extract_table_price(soup, coin_name, price_column)
        
        if price:
            return price
        
        logger.warning(f"No specific price found for {coin_name}. Trying generic method.")
        return extract_generic_price(soup, coin_name)
        
    except Exception as e:
        logger.error(f"Error scraping price for {coin_name}: {e}")
        return None

def extract_table_price(soup, coin_name, price_column):
    """Extract price from table based on specified column index"""
    try:
        # Find the price table
        table = soup.find('table', {'aria-labelledby': 'table-title'})
        if not table:
            logger.warning(f"Price table not found for {coin_name}")
            return None
            
        # Find the first row after header (which has the '1+' quantity)
        rows = table.find_all('tr')
        if len(rows) < 2:  # Need at least header + data row
            logger.warning(f"Price rows not found for {coin_name}")
            return None
            
        # First data row (index 1, after the header)
        data_row = rows[1]
        
        # Get the cells in the row
        cells = data_row.find_all('td')
        
        # Check if we have enough cells
        if len(cells) <= price_column:
            logger.warning(f"Not enough cells in the row for {coin_name} (found {len(cells)}, need > {price_column})")
            return None
            
        # Get the specified price column
        price_cell = cells[price_column]
        price_text = price_cell.get_text(strip=True)
        
        # Extract the price
        match = re.search(r'£([\d,]+\.\d+)', price_text)
        if match:
            # Remove commas for proper float conversion
            price = float(match.group(1).replace(',', ''))
            logger.info(f"Found {coin_name} price in table column {price_column}: £{price}")
            return price
            
        logger.warning(f"Could not extract price from text: '{price_text}'")
        return None
    except Exception as e:
        logger.error(f"Error extracting table price for {coin_name}: {e}")
        return None

def extract_generic_price(soup, coin_name):
    """Generic method to extract prices when specific methods fail"""
    try:
        # Look for price patterns in the HTML
        pound_pattern = re.compile(r'£([\d,]+\.\d+)')
        
        # Collect all possible prices
        all_prices = []
        
        # Method 1: Try to find all td elements and check for price
        for td in soup.find_all('td'):
            text = td.get_text(strip=True)
            matches = pound_pattern.findall(text)
            for match in matches:
                try:
                    # Remove commas for proper float conversion
                    price = float(match.replace(',', ''))
                    all_prices.append(price)
                except ValueError:
                    continue
        
        # Method 2: If not found in td elements, search all text
        if not all_prices:
            for element in soup.find_all(text=True):
                matches = pound_pattern.findall(element)
                for match in matches:
                    try:
                        price = float(match.replace(',', ''))
                        all_prices.append(price)
                    except ValueError:
                        continue
        
        # Filter prices based on expected ranges
        if all_prices:
            logger.info(f"Found prices using generic method: {all_prices}")
            
            # Different price ranges for different coins
            if "Sovereign" in coin_name:
                coin_prices = [p for p in all_prices if 500 <= p <= 800]
            elif "Gold Britannia" in coin_name:
                coin_prices = [p for p in all_prices if 1500 <= p <= 3000]
            elif "Silver Britannia" in coin_name:
                coin_prices = [p for p in all_prices if 20 <= p <= 50]
            else:
                coin_prices = []
                
            if coin_prices:
                logger.info(f"Likely {coin_name} price: £{coin_prices[0]}")
                return coin_prices[0]
            elif all_prices:
                logger.warning(f"No prices in {coin_name} range found. Using first price: £{all_prices[0]}")
                return all_prices[0]
        
        logger.warning("No prices found on page")
        return None
        
    except Exception as e:
        logger.error(f"Error in generic price extraction: {e}")
        return None

# For testing this module in isolation
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test each coin
    for coin_id in COINS:
        price, coin_name = update_price(coin_id)
        if price:
            print(f"The current {coin_name} price is: £{price}")
        else:
            print(f"Could not find the price for {coin_name}")