import glob
import os
from datetime import datetime
from portfolio.utils.config import moralis_api_key, log_dir
from portfolio.utils.init import init, log, info
from icecream import ic

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


def call_moralis_api(endpoint: str, wallet_address: str, chain: str):
    moralis_endpoints = {
        "defi": f"/api/v2.2/wallets/{wallet_address}/defi/positions?chain={chain}",
        "tokens": f"/api/v2.2/{wallet_address}/erc20?chain={chain}",
    }
    host = "https://deep-index.moralis.io"
    endpoint = moralis_endpoints[endpoint]
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


def load_last_response(account: str, chain: str):
    # filename = "/Users/macbook-work/Documents/del/log/portfolio/moralis_balances/Solomon_Medium_polygon_2024-12-08_11_11_02.json"
    # ic(account, chain)
    output_dir = os.path.join(log_dir, "moralis_balances")
    os.makedirs(output_dir, exist_ok=True)
    filespec = os.path.join(output_dir, f"{account.replace(' ','_')}_{chain}_*.json")
    list_of_files = glob.glob(filespec)
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    ic(latest_file)
    with open(latest_file, "r") as f:
        response = json.loads(f.read())
    return response


if __name__ == "__main__":
    init()
    account = "Solomon Medium"
    chain = "polygon"
    endpoint = "defi"
    wallet_address = "0x3Cb83df6CF19831ca241159137b75C71D9087294"
    response = call_moralis_api(endpoint, wallet_address, chain)
    save_response(response, account, chain)
    # response = load_last_response()
