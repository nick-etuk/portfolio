from portfolio.calc.changes.change_over_time import get_change_overtime
from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from icecream import ic


def get_wallet_totals():
    sql = """
    select iif(p.product_id=3, 1, 2) as sort_order,
    act.run_id, act.timestamp, act.amount,
    ac.account_id, ac.descr as account, 
    p.product_id, p.descr as product, p.chain
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join account ac
    on ac.account_id=act.account_id
    where act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and act.status='A'
    -- and act.dummy='N'
    -- and (p.product_id='3' or p.data_source='MORALIS_TOKEN_API')
    and p.cash='Y'
    and act.amount > 10
    order by ac.account_id, sort_order, act.amount desc
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    results = []
    for row in rows:
        changes = get_change_overtime(
            run_id=row.run_id,
            account_id=row.account_id,
            product_id=row.product_id,
            amount=row.amount,
            timestamp_str=row.timestamp,
        )
        results.append(
            {
                "account": row.account,
                "product": row.product,
                "chain": row.chain,
                "amount": row.amount,
                "change": changes.last_run,
                "weekly": changes.weekly,
                "monthly": changes.monthly,
                "alltime": changes.alltime,
            }
        )
    return results
