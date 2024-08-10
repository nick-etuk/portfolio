import os
import sqlite3 as sl
from portfolio.utils.config import db, log_dir

from portfolio.utils.lib import named_tuple_factory

from datetime import datetime
from portfolio.utils.config import moralis_api_key
from portfolio.utils.init import init
from icecream import ic

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


def fetch_balances(wallet_address: str, chain: str):
    """
curl -X 'GET' \
'https://deep-index.moralis.io/api/v2.2/wallets/0x3cb83df6cf19831ca241159137b75c71d9087294/defi/positions?chain=polygon' \
-H 'accept: application/json' \
--header 'X-API-Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjZjOTc2YTg5LTBkNmYtNDEzNy04MDg1LWU5ZDkyMWZjZWFjNSIsIm9yZ0lkIjoiMjU1Mjg3IiwidXNlcklkIjoiMjU5MDg1IiwidHlwZUlkIjoiNjU1NTg5ZjAtOTAwMC00NDY3LWFhZGMtZDRlNDE3ZTk5MTAxIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MjI3MDA0NDQsImV4cCI6NDg3ODQ2MDQ0NH0.vKbhA1wUakQ0syKnREahurq5lIoq5_251DqamYjQ3DE'

curl --request GET \
     --url 'https://deep-index.moralis.io/api/v2.2/wallets/0x3cb83df6cf19831ca241159137b75c71d9087294/defi/positions?chain=polygon' \
     --header 'accept: application/json' \
     --header 'X-API-Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjZjOTc2YTg5LTBkNmYtNDEzNy04MDg1LWU5ZDkyMWZjZWFjNSIsIm9yZ0lkIjoiMjU1Mjg3IiwidXNlcklkIjoiMjU5MDg1IiwidHlwZUlkIjoiNjU1NTg5ZjAtOTAwMC00NDY3LWFhZGMtZDRlNDE3ZTk5MTAxIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MjI3MDA0NDQsImV4cCI6NDg3ODQ2MDQ0NH0.vKbhA1wUakQ0syKnREahurq5lIoq5_251DqamYjQ3DE' 


     /{address}/erc20
    """
    host = "https://api.covalenthq.com"
    wallet_address = "0x3Cb83df6CF19831ca241159137b75C71D9087294"
    endpoint = f"/v1/{chain}/address/{wallet_address}/balances_v2"
    parameters = {"key": covalent_api_key, "quote-currency": "USD"}
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


def extract_balances(response: object, account: str, chain: str):
    # ic(response)

    for item in response["data"]["items"]:
        type = item["type"]
        is_spam = item["is_spam"]
        instrument = item["contract_ticker_symbol"]
        if is_spam or type == "dust":  # or instrument.lower().startswith("claim on"):
            continue
        if instrument.lower().startswith("samm"):
            ic(item)

        decimals = item["contract_decimals"]
        balance_str = item["balance"]
        balance = int(balance_str) / 10**decimals
        balance_usd = item["quote_24h"]
        print(
            f"{account} \t {chain} \t {instrument} \t\t\t {balance} \t\t {balance_usd}"
        )


def save_response(response: object, account: str, chain: str) -> str:
    output_dir = os.path.join(log_dir, "covalent_balances")
    os.makedirs(output_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    filename = os.path.join(
        output_dir, f"{account.replace(' ','_')}_{chain}_{timestamp_str}.json"
    )
    with open(filename, "w") as f:
        f.write(json.dumps(response))
    return ic(filename)


def load_last_response():
    filename = "/Users/macbook-work/Documents/del/log/portfolio/covalent_balances/Solomon_Medium_fantom-mainnet_2024-05-26_16_49_39.json"
    with open(filename, "r") as f:
        response = json.loads(f.read())
    return response


def test_api():
    account = "Solomon Medium"
    chain = "fantom-mainnet"
    wallet_address = "0x3Cb83df6CF19831ca241159137b75C71D9087294"

    # response = fetch_balances(wallet_address, chain)
    response = load_last_response()
    save_response(response, account, chain)
    extract_balances(response, account, chain)


def get_price(symbol: str):
    response = call_covalent_api(symbol)
    if "data" not in response:
        print(f"=>api.get_price: No Coin Market Cap API data for {symbol}")
        return 0
    price_data = response["data"][symbol.upper()]
    # ic(price_data)
    if price_data:
        price_str = price_data[0]["quote"]["USD"]["price"]
        price = float(price_str)

    return price


def get_multiple_prices(symbols: str):
    result = {}
    response = call_cmc_api(symbols)
    # ic(response)
    if "data" not in response:
        print(f"api.get_multiple_prices: No Coin Market Cap API data for {symbols}")
        return {}
    for symbol in symbols.split(","):
        price_data = response["data"][symbol]
        # ic(price_data)
        if price_data:
            price_str = price_data[0]["quote"]["USD"]["price"]
            price = float(price_str) if price_str else 0
            result[symbol] = price

    return result


def get_value(account_id, product_id, product):
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
        "price": round(price, 1),
        "units": round(units, 1),
        "value": round(price * float(units)),
    }


if __name__ == "__main__":
    init()
    print(cmc_get_value(account_id=1, product_id="STG", product=""))
    # print(cmc_get_value(account_id=2, product_id='GHNY', product=''))
    # print(cmc_get_value(account_id=6, product_id='FTT', product=''))
