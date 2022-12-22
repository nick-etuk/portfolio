import sqlite3 as sl
from config import db, html_dir

from lib import named_tuple_factory

from datetime import datetime
from config import cmc_api_key
from init import init
from icecream import ic

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


def call_cmc_api(symbols: str):
    '''
    url = 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
        'start': '1',
        'limit': '5000',
        'convert': coin
    }
    '''
    url = 'https://pro-api.coinmarketcap.com/'
    endpoint = 'v2/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': symbols,
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': cmc_api_key,
    }

    session = Session()
    session.headers.update(headers)

    price = 0
    try:
        response = session.get(url+endpoint, params=parameters)
        return json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def get_price(symbol: str):
    response = call_cmc_api(symbol)
    if 'data' not in response:
        print(f"No CMC API data for {symbol}")
        return 0
    price_data = response['data'][symbol.upper()]
    # ic(price_data)
    if price_data:
        price_str = price_data[0]['quote']['USD']['price']
        price = float(price_str)

    return price


def get_multiple_prices(symbols: str):
    result = {}
    response = call_cmc_api(symbols)
    # ic(response)
    if 'data' not in response:
        print(f"No CMC API data for {symbols}")
        return {}
    for symbol in symbols.split(','):
        price_data = response['data'][symbol]
        # ic(price_data)
        if price_data:
            price_str = price_data[0]['quote']['USD']['price']
            price = float(price_str)
            result[symbol] = price

    return result


def cmc_get_value(account_id, product_id, product):

    price = get_price(product_id)

    sql = """
    Select ac.units
    from actual_total ac
    where seq = (
        select max(seq) from actual_total
        where account_id=ac.account_id
        and product_id=ac.product_id
    )
    and account_id=?
    and product_id=?
    and status='A'
    """
    units = 0
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (account_id, product_id,)).fetchone()

        if row:
            units = row.units

    return {
        'price': round(price, 1),
        'units': round(units, 1),
        'value': round(price*float(units))
    }


if __name__ == "__main__":
    init()
    print(cmc_get_value(account_id=1, product_id='STG', product=''))
    #print(cmc_get_value(account_id=2, product_id='GHNY', product=''))
    #print(cmc_get_value(account_id=6, product_id='FTT', product=''))
