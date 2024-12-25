import inspect
import sqlite3 as sl
from portfolio.services.api.moralis.wallet_chains import get_wallet_chains
from portfolio.utils.config import db
from portfolio.utils.init import warn
from portfolio.utils.lib import named_tuple_factory
from icecream import ic


moralis_chain = {
    "arbitrum": "arbitrum",
    "avalanche": "avalanche",
    "bsc": "bsc",
    "eth": "eth",
    "ftm": "fantom",
    "matic": "polygon",
    "op": "optimism",
}

moralis_wallet_chains = get_wallet_chains()


def moralis_chain_reverse_lookup(lookup_value):
    try:
        key = next(key for key, value in moralis_chain.items() if value == lookup_value)
    except StopIteration:
        calling_function = inspect.stack()[1][3]
        warn(
            f"{calling_function} moralis_chain_reverse_lookup: value {lookup_value} not found"
        )
        key = None
    return key


spam_indicators = [
    "visit",
    "claim",
    "rewards",
    "free",
    "bonus",
    "win",
    "prize",
    "gift",
    "lottery",
    "jackpot",
    "free",
    "freebie",
    "freebies",
    "freebtc",
    "freecrypto",
    "freecoins",
    "freeloot",
    "freemoney",
]

excluded_symbols = [
    "PKT",
    "wMEMO",
    "XEC",
    "MaticSlot",
    "am3CRV-gauge",
    "aAvaWAVAX",
    "FLIP",
]

swap_symbol_names = {
    "USDt": "USDT",
}

stable_coins = [
    "USDT",
    "USDC",
    "DAI",
    "BUSD",
    "TUSD",
    "sUSD",
    "mUSD",
    "USDP",
    "FRAX",
    "FRAX",
    "UST",
    "LUSD",
    "USDN",
    "USTC",
    "FEI",
    "IRON",
    "DSD",
    "ESD",
    "sEUR",
    "sGBP",
    "sCHF",
    "sJPY",
    "sAUD",
    "sCAD",
    "sKRW",
    "sCNY",
    "sRUB",
    "sMXN",
    "sBRL",
    "sSGD",
    "sHKD",
    "sNZD",
    "sSEK",
    "sNOK",
    "sDKK",
    "sZAR",
    "sINR",
    "sAED",
    "sSAR",
    "sQAR",
    "sKWD",
    "sBHD",
    "sOMR",
    "sXAU",
    "sXAG",
    "sXPT",
    "sXPD",
    "sXBR",
    "sXCU",
    "sXAG",
    "sXAU",
    "sXPD",
    "sXPT",
    "sXBR",
    "sXCU",
    "sXAG",
    "sXAU",
    "sXPD",
    "sXPT",
    "sXBR",
    "sXCU",
    "sXAG",
    "sXAU",
    "sXPD",
    "sXPT",
    "sXBR",
    "sXCU",
    "sXAG",
    "sXAU",
    "sXPD",
    "sXPT",
    "sXBR",
    "sXCU",
    "sXAG",
    "sXAU",
    "sXPD",
    "sXPT",
    "sXBR",
    "sXCU",
    "sXAG",
    "sXAU",
    "sXPD",
    "sXPT",
    "sXBR",
    "sXCU",
    "sXAG",
    "sXAU",
    "sXPD",
]

existing_moralis_products = []
product_sql = """
select descr as product
from product
where data_source = 'MORALIS_TOKEN_API'
"""
with sl.connect(db) as conn:
    conn.row_factory = named_tuple_factory
    c = conn.cursor()
    rows = c.execute(product_sql).fetchall()
    for row in rows:
        existing_moralis_products.append(row.product)
