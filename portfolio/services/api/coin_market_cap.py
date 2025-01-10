import sqlite3 as sl
from portfolio.utils.config import db, output_dir

from portfolio.utils.lib import named_tuple_factory

from datetime import datetime
from portfolio.utils.config import cmc_api_key
from portfolio.utils.init import init, warn
from icecream import ic

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


def call_cmc_api(symbols: str):
    """
    url = 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
        'start': '1',
        'limit': '5000',
        'convert': coin
    }
    """
    url = "https://pro-api.coinmarketcap.com/"
    endpoint = "v2/cryptocurrency/quotes/latest"
    parameters = {"symbol": symbols, "convert": "USD"}
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": cmc_api_key,
    }

    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url + endpoint, params=parameters)
        return json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def get_price(symbol: str):
    response = call_cmc_api(symbol)
    if "data" not in response:
        warn(f"=>api.get_price: No Coin Market Cap API data for {symbol}")
        return 0
    price_data = response["data"][symbol.upper()]
    # ic(price_data)
    if price_data:
        price_str = price_data[0]["quote"]["USD"]["price"]
        price = float(price_str)

    return price


def get_multiple_prices(symbols: str):
    # symbols is a comma separated list of symbols
    result = {}
    response = call_cmc_api(symbols)
    # ic(response)
    if "data" not in response:
        print(f"No Coin Market Cap API data for {symbols}")
        print(response)
        return None
    for symbol in symbols.split(","):
        if symbol not in response["data"]:
            # warn(f"bp 2 No Coin Market Cap API data for {symbol}")
            continue
        price_data = response["data"][symbol]
        # ic(price_data)
        if price_data:
            price_str = price_data[0]["quote"]["USD"]["price"]
            price = float(price_str) if price_str else 0
            result[symbol] = price

    return result


def cmc_get_value(run_mode, account_id, product_id, product):
    price = get_price(product_id)

    sql = """
    Select act.units
    from actual_total act
    where seq = (
        select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
    )
    and account_id=?
    and product_id=?
    and status='A'
    """
    units = 0
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(
            sql,
            (
                account_id,
                product_id,
            ),
        ).fetchone()

        if row:
            units = row.units

    return {
        "price": price,
        "units": units,
        "value": price * float(units),
    }


if __name__ == "__main__":
    init()
    print(cmc_get_value(account_id=1, product_id="STG", product=""))
    # print(cmc_get_value(account_id=2, product_id='GHNY', product=''))
    # print(cmc_get_value(account_id=6, product_id='FTT', product=''))
