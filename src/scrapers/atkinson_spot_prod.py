"""
Atkinsons website scraper for precious metals spot prices
"""
import requests
from bs4 import BeautifulSoup
import re
import logging
from metals_spot import ATKINSONS_SPOT  # Import from config

logger = logging.getLogger('price_scraper')

def get_all_prices(output_type=None):
    """
    Fetch prices for all precious metals from Atkinsons
    
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
    for metal_symbol in ATKINSONS_SPOT:
        price, metal_name = update_price(metal_symbol)
        if price:
            results[metal_symbol] = {
                "price": price,
                "name": metal_name
            }
            
            # Print results if logging mode is active
            if output_type == "logging":
                print(f"The current {metal_name} price is: £{price}")
        elif output_type == "logging":
            print(f"Could not find the price for {metal_name}")
    
    return results

def update_price(metal_symbol):
    """Fetch the price for a specific coin"""
    if metal_symbol not in ATKINSONS_SPOT:
        logger.error(f"Unknown precious metal symbol: {metal_symbol}")
        return None, None
        
    url = ATKINSONS_SPOT[metal_symbol][0]
    metal_name = ATKINSONS_SPOT[metal_symbol][1]
    class_name = ATKINSONS_SPOT[metal_symbol][2]
    
    price = scrape_atkinsons_spot_price(url, metal_name, class_name)
    
    if price:
        logger.info(f"Successfully scraped {metal_name} price: £{price}")
        return price, metal_name
    else:
        logger.error(f"Failed to scrape {metal_name} price")
        return None, metal_name

def scrape_atkinsons_spot_price(url, metal_name, class_name):
    """Scrape the price from the Atkinsons homepage"""
    try:
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.atkinsonsbullion.com/'
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
        return extract_table_price(soup, metal_name, class_name)
        
    except Exception as e:
        logger.error(f"Error scraping price for {metal_name}: {e}")
        return None

def extract_table_price(soup, metal_name, class_name):

    """
    Extract spot price from table for specified metal and price type.
    
    Args:
        soup: BeautifulSoup object containing the webpage
        metal_name: String, either 'gold' or 'silver'
        class_name: String, CSS class name for the price cell
    
    Returns:
        Float: The price value or None if not found
    """
    try:
        # First, find the specific price table
        table = soup.find('table', {'data-lp': 'spotPrice'})
        if not table:
            logger.warning(f"Price table not found for {metal_name}")
            return None
        
        # Try to find the price cell directly using the class name
        price_cell = soup.find('td', class_=class_name)

        # # If direct class lookup failed, try alternative methods
        # if not price_cell:
        #     logger.warning(f"Could not find price cell with class '{class_name}', trying alternative methods")
            
        #     # Method 2: Find the price table
        #     table = soup.find('table', {'data-lp': 'spotPrice'})
        #     if not table:
        #         logger.warning(f"Price table not found for {metal_name}")
        #         return None
                
        #     # Try to find the row containing the metal name
        #     metal_row = None
        #     for row in table.find_all('tr'):
        #         th = row.find('th')
        #         if th and metal_name.lower() in th.text.lower():
        #             metal_row = row
        #             break

        #     # Method 3: If still not found, try by index
        #     if not metal_row:
        #         rows = table.find_all('tr')
        #         if metal_name.lower() == 'gold' and len(rows) > 1:
        #             metal_row = rows[1]  # Gold is first data row
        #         elif metal_name.lower() == 'silver' and len(rows) > 2:
        #             metal_row = rows[2]  # Silver is second data row
        #         else:
        #             logger.warning(f"Row for {metal_name} not found")
        #             return None
            
        #     # Extract price cell based on suffix in class_name
        #     cells = metal_row.find_all('td')
        #     if not cells:
        #         logger.warning(f"No price cells found for {metal_name}")
        #         return None
                
        #     # Determine which cell to use based on class_name suffix
        #     cell_index = 0  # Default to troy ounce
        #     if 'grams' in class_name:
        #         cell_index = 1  # Use gram price
                
        #     if cell_index >= len(cells):
        #         logger.warning(f"Price cell index {cell_index} out of range")
        #         return None
            
        #     price_cell = cells[cell_index]  # Set price_cell to the cell we found
        
       
        price_text = price_cell.get_text(strip=True)
        return price_cell
        # if not price_text:
        #     logger.warning("Price cell contains no text (possibly a loading SVG)")
        #     return None
   
        # # Extract the price
        # match = re.search(r'£([\d,]+\.\d+)', price_text)
        # if match:
        #     # Remove commas for proper float conversion
        #     price = float(match.group(1).replace(',', ''))
        #     logger.info(f"Found {metal_name} price: £{price}")
        #     return price
            
        logger.warning(f"Could not extract price from text: '{price_text}'")
        return None
    except Exception as e:
        logger.error(f"Error extracting table price for {metal_name}: {e}")
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