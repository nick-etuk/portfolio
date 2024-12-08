"""
Covelent now goldrush.
Now costs $250 per month minimum.
"""

from covalent import CovalentClient

# from portfolio.utils.config import covalent_api_key
from icecream import ic


def covalent_api():
    solomon_med = "0x3Cb83df6CF19831ca241159137b75C71D9087294"
    solomon_high = "0xEc10A8061dAeBdA85386dBf16E9880706bC9f1b9"
    covalent_api_key = "cqt_rQpwkM8v7yrp8BXCRWYq3rFBqBPP"

    c = CovalentClient(covalent_api_key)
    response = c.balance_service.get_token_balances_for_wallet_address(
        # chain_name="eth-mainnet", wallet_address="demo.eth"
        # chain_name="fantom-mainnet",
        chain_name="eth-mainnet",
        # wallet_address=solomon_med,
        wallet_address="demo.eth",
    )
    ic(response.data)
    if not response.error:
        print(response.data)
    else:
        print(response.error_message)


if __name__ == "__main__":
    solomon_med = "0x3Cb83df6CF19831ca241159137b75C71D9087294"
    solomon_high = "0xEc10A8061dAeBdA85386dBf16E9880706bC9f1b9"
    """
    Solomon LTC
    0x6b707Ab93B8153c930aBfaa709087772DDCcc8e6

    Peronsal Med
    0x5B19bAeb7491Ad1890dD6F1A41b935aa11C0cFf7

    Personal High
    0xb9CD1949B934897ABA4EB107853C3D2BfcB225De

    Personal LTC
    0x541A1f804aC641A07DD719CC0A9Ca89a7F8F756E

    https://api.covalenthq.com/v1/1/address/0xB1AdceddB2941033a090dD166a462fe1c2029484/stacks/compound/acts/?key=cqt_rQpwkM8v7yrp8BXCRWYq3rFBqBPP
    
    curl -X GET https://api.covalenthq.com/v1/fantom-mainnet/address/0x3Cb83df6CF19831ca241159137b75C71D9087294/balances_v2/?key=cqt_rQpwkM8v7yrp8BXCRWYq3rFBqBPP \
    -H 'Content-Type: application/json' \
    -u YOUR_API_KEY: \

    """
    covalent_api()
