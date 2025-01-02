import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from portfolio.services.api.moralis.call_api import (
    call_moralis_api,
    load_last_response,
    save_response,
)
from portfolio.services.api.moralis.moralis_config import moralis_chain
from portfolio.utils.init import init, log, info
from icecream import ic


def extract_balances(response: object, account: str, chain: str):
    for protocol in response:
        instrument = protocol["protocol_name"]
        position = protocol["position"]
        balance_usd = position["balance_usd"]
        info(f"MORALIS API Defi: {account} \t {chain} \t {instrument} \t\t\t {balance_usd}")
        return balance_usd


def moralis_defi_balance(run_mode, account_id, product_id, product):
    sql = """
    select ac.address, ac.descr as account,
    p.chain,
    act.amount as old_amount
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product p
    on p.product_id=act.product_id
    where act.account_id=?
    and p.product_id=?
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        )
    and act.status='A'
    """
    # account = "Solomon Medium"
    # chain = "polygon"
    # wallet_address = "0x3Cb83df6CF19831ca241159137b75C71D9087294"

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (account_id, product_id)).fetchone()

    chain = moralis_chain[row.chain]
    if run_mode == "dry_run":
        response = load_last_response(account=row.account, chain=chain)
    else:
        response = call_moralis_api(
            endpoint="defi", wallet_address=row.address, chain=chain
        )
        save_response(response, f"defi_{row.account}", row.chain)

    amount = extract_balances(response, row.account, row.chain)
    return {"price": 0, "units": 0, "value": amount}


if __name__ == "__main__":
    init()
    # print(cmc_get_value(account_id=2, product_id='GHNY', product=''))
    # print(cmc_get_value(account_id=6, product_id='FTT', product=''))
