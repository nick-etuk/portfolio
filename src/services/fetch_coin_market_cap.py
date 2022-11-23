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


def get_price(symbol: str):
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
        'symbol': symbol,
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
        data = json.loads(response.text)
        price = data['data'][symbol][0]['quote']['USD']['price']
        price = float(price)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return price


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
