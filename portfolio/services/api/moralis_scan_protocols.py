import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import (
    named_tuple_factory,
)
from portfolio.utils.init import init, log
from portfolio.services.api.moralis import (
    fetch_balances,
    save_response,
    extract_balances,
)
from icecream import ic


def scan_moralis_protocols():
    sql = """
        select distinct ac.account_id, ac.descr as account, ac.address,
        p.product_id, p.descr as product, p.chain
        from actual_total act
        inner join account ac
        on ac.account_id=act.account_id
        inner join product p
        on p.product_id=act.product_id
        where act.seq=
            (select max(seq) from actual_total
            where account_id=act.account_id
            and product_id=act.product_id
            )
        and act.status='A'
        and ac.address <> ''
        and p.chain not in (' ', 'none')
        and p.data_source in ('HTML')
        """

    moralis_chain = {
        "avalanche": "avalanche",
        "ftm": "fantom",
        "eth": "ethereum",
        "bsc": "bsc",
        "matic": "polygon",
        "op": "optimism",
    }

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    for row in rows:
        chain = moralis_chain[row.chain]
        log(f"{row.account} {row.product} on {chain}")

        response = fetch_balances(row.address, chain)
        if response:
            log("New balance found on Moralis")
            save_response(response, row.account, chain)
            extract_balances(response, row.account, chain)


if __name__ == "__main__":
    init()
    scan_moralis_protocols()
