import re
import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from portfolio.services.api.moralis.moralis_config import (
    moralis_chains,
    moralis_chain_reverse_convertion,
    spam_indicators,
    excluded_symbols,
    swap_symbol_names,
    existing_moralis_products,
)
from portfolio.services.api.moralis.call_api import call_moralis_api, save_response
from portfolio.services.api.moralis.add_cmc_prices import add_cmc_prices
from portfolio.utils.init import init, log, info, warn
from icecream import ic


def save_moralis_product(symbol_name, chain):
    insert_sql = """
    insert into product (product_id, descr, data_source, chain, volatile) 
    values (?, ?, ?, 'Y')
    """

    if symbol_name in existing_moralis_products:
        return

    existing_moralis_products.append(symbol_name)

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(
            insert_sql,
            (symbol_name, symbol_name, "MORALIS_TOKEN_API", chain),
        )
        conn.commit()


def save_balances(account_id, account, symbols: dict):
    insert_sql = """
    insert into actual_total (
        account_id, product_id, seq, amount, units, price, status
    ) values (
        ?, 
        ?, 
        (select max(seq) + 1 from actual_total where account_id=? and product_id=?), 
        ?, 
        ?, 
        'A'
    )
    """

    for symbol_name in symbols:
        symbol = symbols[symbol_name]
        if "value" not in symbol:
            warn(f"Symbol {symbol_name} has no value")
            ic(symbol)
            continue
        if account == "Old Personal Medium" and symbol_name == "BUSD":
            # Incorrect value from Moralis token API for Old Personal Medium 	 BUSD bsc 	 13006
            continue
        value = symbol["value"]
        if value < 1:
            # print(f"Skipping {symbol_name} with value {value}")
            continue
        info(
            f"Moralis token API: {account} \t {symbol_name} {symbol['chain']} \t {value}"
        )
        continue
        save_moralis_product(symbol_name, symbol["chain"])
        with sl.connect(db) as conn:
            conn.row_factory = named_tuple_factory
            c = conn.cursor()
            c.execute(
                insert_sql,
                (
                    account_id,
                    symbol_name,
                    symbol["units"],
                    value,
                ),
            )
            conn.commit()


def extract_token_units(response: object, chain: str):
    amount_str = response["balance"]
    if amount_str and "decimals" in response:
        decimals = response["decimals"]
        # insert decimal point into amount_str at position len(amount_str) - decimals
        # amount = float(
        #     amount_str[: len(amount_str) - decimals] + "." + amount_str[-decimals:]
        # )
        units = int(amount_str) / 10**decimals

        symbol_name = response["symbol"]

        if any(spam in symbol_name.lower() for spam in spam_indicators):
            # log(f"Spam: {symbol_name}")
            return None
        valid_symbol_name = re.match("^[\w-]+$", symbol_name) is not None
        if not valid_symbol_name or symbol_name in excluded_symbols:
            # log(f"Invalid symbol {symbol}")
            return None

        if symbol_name in swap_symbol_names:
            symbol_name = swap_symbol_names[symbol_name]

        my_chain = moralis_chain_reverse_convertion[chain]
        return {"symbol": symbol_name, "units": units, "chain": my_chain}


def moralis_wallet_token_values():
    account_sql = """
    select ac.account_id, ac.address, ac.descr as account
    from account ac
    where ac.address <> ' '
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        account_rows = c.execute(account_sql).fetchall()

    for account_row in account_rows:
        symbols = {}
        for chain in moralis_chains:
            # info(f"{account_row.account} {chain}")
            response = call_moralis_api(
                "tokens", wallet_address=account_row.address, chain=chain
            )
            # response = load_last_response()
            if not response:
                continue
            save_response(response, f"tokens_{account_row.account}", chain)
            for response_row in response:
                if "balance" in response_row:
                    token_obj = extract_token_units(response_row, chain)
                    if not token_obj:
                        continue
                    # ic(token_obj)
                    symbol_name = token_obj["symbol"]
                    if symbol_name in symbols:
                        # print(f"Duplicate entry for {symbol_name} on {moralis_chain_reverse_convertion[chain]}")
                        symbols[symbol_name]["units"] += token_obj["units"]
                        # print(f"Incrementing existing units by {token_obj['units']} to {symbols[symbol_name]['units']}")
                        continue
                    symbols[symbol_name] = token_obj

        # ic(symbols)
        symbols_with_prices = add_cmc_prices(symbols)
        # ic(symbols_with_prices)
        save_balances(account_row.account_id, account_row.account, symbols_with_prices)


if __name__ == "__main__":
    init()
    # print(cmc_get_value(account_id=2, product_id='GHNY', product=''))
    # print(cmc_get_value(account_id=6, product_id='FTT', product=''))
