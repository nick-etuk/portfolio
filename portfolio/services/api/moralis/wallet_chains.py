import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.init import warn
from portfolio.utils.lib import named_tuple_factory
from icecream import ic


def get_wallet_chains():
    """
    Warning - this will not scan for new chains,
    but will reduce calls to moralis API.
    """
    sql = """
    select ac.account_id, ac.descr as account,
    p.descr as product, p.chain
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product p
    on p.product_id=act.product_id
    where act.seq=(
        select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        )
    and ac.address <> ' '
    and p.data_source like 'MORALIS%'
    order by ac.account_id, p.product_id
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    chains = {}
    for row in rows:
        if row.account_id not in chains:
            chains[row.account_id] = [row.chain]
            continue
        if row.chain in chains[row.account_id]:
            continue
        chains[row.account_id].append(row.chain)

    ic(chains)
    return chains
