from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from icecream import ic


def product_too_high_risk(combined_total: float):
    """
    Product too high risk for account.
    """

    sql = """
    select ac.account_id, p.product_id, p.descr as product, act.amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join account ac
    on ac.account_id = ac.account_id
    inner join risk_category risk
    on risk.id = p.risk_category
    inner join instrument_status inst
    on inst.account_id=act.account_id
    and inst.product_id=act.product_id
    where act.status='A'
    and risk.risk_level > ac.max_risk
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and inst.effdt=(
        select max(effdt) from instrument_status
        where account_id=inst.account_id
        and product_id=inst.product_id
    )
    """
    instances = []
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    if rows:
        for row in rows:
            instances.append(f"{row.product}. Reduce by {round(row.amount)}")

    return instances
