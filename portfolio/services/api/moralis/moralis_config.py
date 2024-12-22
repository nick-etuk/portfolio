import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from icecream import ic

moralis_chains = [
    "arbitrum",
    "avalanche",
    "bsc",
    "eth",
    "fantom",
    "polygon",
    "optimism",
]

moralis_chain_convertion = {
    "avalanche": "avalanche",
    "ftm": "fantom",
    "eth": "eth",
    "bsc": "bsc",
    "matic": "polygon",
    "op": "optimism",
    "arbitrum": "arbitrum",
}

moralis_chain_reverse_convertion = {
    "avalanche": "avalanche",
    "fantom": "ftm",
    "eth": "eth",
    "bsc": "bsc",
    "polygon": "matic",
    "optimism": "op",
    "arbitrum": "arbitrum",
}

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

ic(existing_moralis_products)
