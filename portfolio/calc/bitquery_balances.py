from datetime import datetime
import json
import os
import sqlite3 as sl
from icecream import ic
from portfolio.utils.config import db, raw_html_dir, data_dir
from portfolio.utils.lib import named_tuple_factory
from portfolio.services.api.bitquery import get_wallet_balances
from portfolio.services.api.coin_market_cap import get_multiple_prices

result = []


def bitquery_balances():
    """
    Get cash balances from Bitquery API
    Is this really just cash balances, or is it all balances for each account?
    """
    output_dir = os.path.join(data_dir, "bitquery_balances")
    chains = ["ethereum", "bsc", "matic", "fantom", "avalanche", "moonbeam"]
    # Exclude shit coins with same symbol as legitimate coins
    exclusion_list = ["BUSDSWAP.NET"]
    symbols = []
    amounts = {}

    sql = """
        select ac.account_id, ac.descr as account, ac.address
        from account ac
        where ac.address <> ' '
        """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    for row in rows:
        # if row.account != "Old Personal Medium": continue
        amounts[row.account] = {}
        response = get_wallet_balances(row.address)

        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        filename = f"{row.account}_{timestamp_str}.json"
        # filename = "Old Personal Medium_2022-12-01_10_47_22.json"
        # with open(os.path.join(raw_html_dir, filename), 'r') as f:
        #   response = json.load(f)

        with open(os.path.join(output_dir, filename), "w") as f:
            f.write(json.dumps(response))

        for chain in chains:
            amounts[row.account][chain] = {}
            address_list = response["data"][chain + "_network"]["address"]
            for address_item in address_list:
                balance_list = address_item["balances"]
                if balance_list:
                    for balance_object in balance_list:
                        name = balance_object["currency"]["name"]
                        if name in exclusion_list:
                            print(f"Excluding {name}")
                            continue
                        amount = balance_object["value"]
                        symbol = balance_object["currency"]["symbol"].upper()
                        if (
                            float(amount) != 0
                            and not " " in symbol
                            and not "." in symbol
                            and not "-" in symbol
                        ):
                            amounts[row.account][chain][symbol] = amount
                            if symbol not in symbols:
                                symbols.append(symbol)

    if not symbols:
        return []
    symbols_str = ",".join(symbols)
    prices = get_multiple_prices(symbols_str)
    # ic(symbols_str)
    # ic(prices)
    # ic(amounts)
    for account in amounts:
        for chain in amounts[account]:
            for symbol in amounts[account][chain]:
                amount = amounts[account][chain][symbol]

                if symbol not in prices:
                    print(
                        f"=>get_cash_balances: No prices for {symbol} from Coin Market Cap"
                    )
                    continue

                value = prices[symbol] * amount

                if value > 10:
                    print(f"{account} {chain} {symbol} {value}")
                    result.append([account, chain, symbol, round(value)])

    print("bitquery balances:", result)
    return result


if __name__ == "__main__":
    bitquery_balances()
