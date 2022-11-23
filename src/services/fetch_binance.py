from datetime import datetime
from binance.spot import Spot

from config import binance_api_key, binance_api_secret
from init import init
from icecream import ic


def binance_balance(account_id, product_id, product):

    asset_lookup = {'Binance Earn BUSD': 'BUSD', 'Binance Earn BNB': 'BNB'}
    client = Spot(key=binance_api_key, secret=binance_api_secret)
    result = client.savings_account()
    total = 0
    for position in result['positionAmountVos']:
        if position['asset'] == asset_lookup[product]:
            total += float(position['amountInUSDT'])

    return {'price': 0, 'units': 0, 'value': round(total)}


if __name__ == "__main__":
    init()
    print(binance_balance())
