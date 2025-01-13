import os
import sqlite3 as sl
from portfolio.utils.config import db, log_dir

from portfolio.utils.lib import named_tuple_factory

from datetime import datetime
from portfolio.utils.config import exchange_rate_api_key
from portfolio.utils.init import info, init, warn
from icecream import ic

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


def call_exchange_rate_api():
    """
    curl -X GET https://v6.exchangerate-api.com/v6/f90cb703452638efbdb6d0f2/latest/USD  \
    -H 'Content-Type: application/json' \
    -u YOUR_API_KEY: \
    """
    host = "https://v6.exchangerate-api.com"
    endpoint = f"/v6/{exchange_rate_api_key}/latest/USD"
    parameters = {}
    headers = {
        "Accepts": "application/json",
    }

    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(f"{host}{endpoint}/", params=parameters)
        return json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def extract_exchange_rate(response: object, currency: str):
    if currency not in response["conversion_rates"]:
        warn(f"exchange_rate_api: No conversion rate for {currency}")
        ic(response)
        return 0
    
    rate = response["conversion_rates"][currency]
    info(f"exchange_rate_api: {currency} \t {rate}")
    return rate


def save_response(response: object, filename: str) -> str:
    with open(filename, "w") as f:
        f.write(json.dumps(response))


def get_exchange_rate(run_mode, account_id, product_id, product):
    sql = """
    Select act.units, act.price
    from actual_total act
    where seq = (
        select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
    )
    and act.account_id=?
    and act.product_id=?
    and act.status='A'
    """

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql,(account_id, product_id)).fetchone()

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(log_dir, f"exchange_rates_{date_str}.json")
    if os.path.exists(filename):
        with open(filename, "r") as f:
            response = json.load(f)
    else:
        response = call_exchange_rate_api()
        save_response(response, filename)

    if "conversion_rates" not in response:
        print(f"exchange_rate_api: No conversion rates in response")
        return None
    
    rate = extract_exchange_rate(response=response, currency=product_id)
    return {
        "price": rate,
        "units": row.units,
        "value": rate * float(row.units),
    }


if __name__ == "__main__":
    init()
    print(get_exchange_rate(run_mode="normal", account_id=1, product_id="GBP", product=""))
