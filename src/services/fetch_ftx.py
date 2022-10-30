from ftx_client import FtxClient
from config import ftx_api_key, ftx_api_secret
from init import init
from icecream import ic


def ftx_balance(account_id, product):
    client = FtxClient(api_key=ftx_api_key, api_secret=ftx_api_secret)
    result = client.get_all_balances()
    total = 0
    for coin in result['main']:
        total += coin['usdValue']

    return total


if __name__ == "__main__":
    init()
    print(ftx_balance())
