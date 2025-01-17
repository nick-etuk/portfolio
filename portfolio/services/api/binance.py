from datetime import datetime
from binance import Client

from portfolio.utils.config import binance_api_key, binance_api_secret
from portfolio.utils.init import init
from icecream import ic


def binance_balance(account_id, product_id, product):
    client = Client(api_key=binance_api_key, api_secret=binance_api_secret)
    result = client.savings_account()

    asset_lookup = {"Binance Earn BUSD": "BUSD", "Binance Earn BNB": "BNB"}
    total = 0
    for position in result["positionAmountVos"]:
        if position["asset"] == asset_lookup[product]:
            total += float(position["amountInUSDT"])

    return {"price": 0, "units": 0, "value": total}


if __name__ == "__main__":
    init()
    print(binance_balance(0, 0, "BUSD"))
