# In src/main.py
from scrapers.chards_prod import get_all_prices
from scrapers.chards_prod import update_price as chard_update_price
from scrapers.coins import CHARD_COINS

if __name__ == "__main__":
    # get_all_prices("logging")
    # print (get_all_prices())
    sovereign_price, coin_name = chard_update_price("sovereign")
    print(sovereign_price)

    