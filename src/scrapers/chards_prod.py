"""
Chards website scraper for precious metals prices
"""
import requests
from bs4 import BeautifulSoup
import re
import logging
from .coins import CHARD_COINS  # Import from config

logger = logging.getLogger('price_scraper')

def get_all_prices(output_type=None):
    """
    Fetch prices for all CHARD_COINS from Chards
    
    Args:
        output_type (str, optional): If set to "logging", 
                                     will print results like in main. 
                                     Default is None.
    
    Returns:
        dict: Dictionary of coin prices
    """
    # Set up logging if requested
    if output_type == "logging":
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    results = {}
    for coin_id in CHARD_COINS:
        price, coin_name = update_price(coin_id)
        if price:
            results[coin_id] = {
                "price": price,
                "name": coin_name
            }
            
            # Print results if logging mode is active
            if output_type == "logging":
                print(f"The current {coin_name} price is: £{price}")
        elif output_type == "logging":
            print(f"Could not find the price for {coin_name}")
    
    return results

def update_price(coin_id):
    """Fetch the price for a specific coin"""
    if coin_id not in CHARD_COINS:
        logger.error(f"Unknown coin ID: {coin_id}")
        return None, None
        
    url = CHARD_COINS[coin_id][0]
    coin_name = CHARD_COINS[coin_id][1]
    price_column = CHARD_COINS[coin_id][2]
    
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
        
        # Extract price from the table
        return extract_table_price(soup, coin_name, price_column)
        
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

# For testing this module in isolation
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Use the get_all_prices function with logging mode
    get_all_prices("logging")