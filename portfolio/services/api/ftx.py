from portfolio.services.api.ftx_client import FtxClient
from portfolio.utils.config import ftx_api_key, ftx_api_secret
from portfolio.utils.init import init
from icecream import ic


def ftx_balance(account_id, product_id, product):
    client = FtxClient(api_key=ftx_api_key, api_secret=ftx_api_secret)
    result = client.get_all_balances()
    total = 0
    for coin in result['main']:
        total += coin['usdValue']

    return {'price': 0, 'units': 0, 'value': total}


if __name__ == "__main__":
    init()
    print(ftx_balance())
