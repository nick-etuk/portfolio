import os
import sqlite3 as sl
from portfolio.utils.config import db, log_dir

from portfolio.utils.lib import named_tuple_factory

from datetime import datetime
from portfolio.utils.config import moralis_api_key
from portfolio.utils.init import init, log, info
from icecream import ic

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


def call_moralis_api(wallet_address: str, chain: str):
    """
    moralis wallet profit & loss

curl -X 'GET' \
    'https://deep-index.moralis.io/api/v2.2/wallets/0x3cb83df6cf19831ca241159137b75c71d9087294/profitability?chain=eth' \
-H 'accept: application/json' \
--header 'X-API-Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjZjOTc2YTg5LTBkNmYtNDEzNy04MDg1LWU5ZDkyMWZjZWFjNSIsIm9yZ0lkIjoiMjU1Mjg3IiwidXNlcklkIjoiMjU5MDg1IiwidHlwZUlkIjoiNjU1NTg5ZjAtOTAwMC00NDY3LWFhZGMtZDRlNDE3ZTk5MTAxIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MjI3MDA0NDQsImV4cCI6NDg3ODQ2MDQ0NH0.vKbhA1wUakQ0syKnREahurq5lIoq5_251DqamYjQ3DE'

    
    """
    """
curl -X 'GET' \
'https://deep-index.moralis.io/api/v2.2/wallets/0x3cb83df6cf19831ca241159137b75c71d9087294/defi/positions?chain=polygon' \
-H 'accept: application/json' \
--header 'X-API-Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjZjOTc2YTg5LTBkNmYtNDEzNy04MDg1LWU5ZDkyMWZjZWFjNSIsIm9yZ0lkIjoiMjU1Mjg3IiwidXNlcklkIjoiMjU5MDg1IiwidHlwZUlkIjoiNjU1NTg5ZjAtOTAwMC00NDY3LWFhZGMtZDRlNDE3ZTk5MTAxIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MjI3MDA0NDQsImV4cCI6NDg3ODQ2MDQ0NH0.vKbhA1wUakQ0syKnREahurq5lIoq5_251DqamYjQ3DE'

curl --request GET \
     --url 'https://deep-index.moralis.io/api/v2.2/wallets/0x3cb83df6cf19831ca241159137b75c71d9087294/defi/positions?chain=polygon' \
     --header 'accept: application/json' \
     --header 'X-API-Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjZjOTc2YTg5LTBkNmYtNDEzNy04MDg1LWU5ZDkyMWZjZWFjNSIsIm9yZ0lkIjoiMjU1Mjg3IiwidXNlcklkIjoiMjU5MDg1IiwidHlwZUlkIjoiNjU1NTg5ZjAtOTAwMC00NDY3LWFhZGMtZDRlNDE3ZTk5MTAxIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MjI3MDA0NDQsImV4cCI6NDg3ODQ2MDQ0NH0.vKbhA1wUakQ0syKnREahurq5lIoq5_251DqamYjQ3DE' 

    curl --request GET \
     --url 'https://deep-index.moralis.io/api/v2.2/wallets/0x3cb83df6cf19831ca241159137b75c71d9087294/defi/quickswap-v2/positions?chain=polygon' \
     --header 'accept: application/json' \
     --header 'X-API-Key: 
     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjZjOTc2YTg5LTBkNmYtNDEzNy04MDg1LWU5ZDkyMWZjZWFjNSIsIm9yZ0lkIjoiMjU1Mjg3IiwidXNlcklkIjoiMjU5MDg1IiwidHlwZUlkIjoiNjU1NTg5ZjAtOTAwMC00NDY3LWFhZGMtZDRlNDE3ZTk5MTAxIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MjI3MDA0NDQsImV4cCI6NDg3ODQ2MDQ0NH0.vKbhA1wUakQ0syKnREahurq5lIoq5_251DqamYjQ3DE' 


     /{address}/erc20
    
     defi summary endpoint
     ----------------------
     kinda works. only shows uniswap for solomon medium risk.
wallet_address='0x3cb83df6cf19831ca241159137b75c71d9087294'
chain='polygon'
moralis_api_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjZjOTc2YTg5LTBkNmYtNDEzNy04MDg1LWU5ZDkyMWZjZWFjNSIsIm9yZ0lkIjoiMjU1Mjg3IiwidXNlcklkIjoiMjU5MDg1IiwidHlwZUlkIjoiNjU1NTg5ZjAtOTAwMC00NDY3LWFhZGMtZDRlNDE3ZTk5MTAxIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MjI3MDA0NDQsImV4cCI6NDg3ODQ2MDQ0NH0.vKbhA1wUakQ0syKnREahurq5lIoq5_251DqamYjQ3DE'
curl --request GET \
--url "https://deep-index.moralis.io/api/v2.2/wallets/$wallet_address/defi/summary?chain=$chain" \
--header 'accept: application/json' \
--header "X-API-Key: $moralis_api_key"
    """
    # wallet_address = "0x3Cb83df6CF19831ca241159137b75C71D9087294"
    # ic(chain)
    host = "https://deep-index.moralis.io"
    endpoint = f"/api/v2.2/wallets/{wallet_address}/defi/positions?chain={chain}"
    headers = {
        "accept": "application/json",
        "X-API-Key": moralis_api_key,
    }

    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(f"{host}{endpoint}")
        status_code = response.status_code
        # ic(status_code)
        if status_code != 200:
            print(f"Moralis API error {status_code} on chain {chain}:")
            print(f"{response.text}")
            return None

        # ic(response.text)
        return json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def extract_balances(response: object, account: str, chain: str):
    for protocol in response:
        instrument = protocol["protocol_name"]
        position = protocol["position"]
        balance_usd = position["balance_usd"]
        info(f"{account} \t {chain} \t {instrument} \t\t\t {balance_usd}")
        return balance_usd


def save_response(response: object, account: str, chain: str) -> str:
    output_dir = os.path.join(log_dir, "moralis_balances")
    os.makedirs(output_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    filename = os.path.join(
        output_dir, f"{account.replace(' ','_')}_{chain}_{timestamp_str}.json"
    )
    output_str = json.dumps(response, indent=4)
    with open(filename, "w") as f:
        f.write(output_str)
    return filename


def load_last_response():
    filename = "/Users/macbook-work/Documents/del/log/portfolio/moralis_balances/Solomon_Medium_polygon_2024-12-08_11_11_02.json"
    with open(filename, "r") as f:
        response = json.loads(f.read())
    return response


def moralis_balance(account_id, product_id, product):
    sql = """
    select ac.address, ac.descr as account,
    p.chain,
    act.amount as old_amount
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product p
    on p.product_id=act.product_id
    where act.account_id=?
    and p.product_id=?
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        )
    and act.status='A'
    """
    # account = "Solomon Medium"
    # chain = "polygon"
    # wallet_address = "0x3Cb83df6CF19831ca241159137b75C71D9087294"

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (account_id, product_id)).fetchone()

    response = call_moralis_api(wallet_address=row.address, chain=row.chain)
    # response = load_last_response()
    save_response(response, row.account, row.chain)
    amount = extract_balances(response, row.account, row.chain)
    return {"price": 0, "units": 0, "value": amount}


if __name__ == "__main__":
    init()
    # print(cmc_get_value(account_id=2, product_id='GHNY', product=''))
    # print(cmc_get_value(account_id=6, product_id='FTT', product=''))
