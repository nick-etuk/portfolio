# import inspect
from portfolio.services.api.coin_market_cap import get_multiple_prices
from portfolio.utils.init import info, warn
from icecream import ic


def add_cmc_prices(symbols: dict):
    if not symbols:
        return symbols
    symbol_names = ",".join(symbols.keys())
    # ic(symbol_names)
    multiple_prices = get_multiple_prices(symbol_names)
    if not multiple_prices:
        warn(f"No Coin Market Cap API data for {symbol_names}")
        return symbols

    new_dict = {}
    for symbol_name in symbols:
        if symbol_name not in multiple_prices:
            continue
        symbol = symbols[symbol_name]
        price = multiple_prices[symbol_name]
        units = symbol["units"]
        new_item = {
            "symbol": symbol_name,
            "chain": symbol["chain"],
            "units": units,
            "price": price,
            "value": units * price,
        }
        new_dict[symbol_name] = new_item
    return new_dict
