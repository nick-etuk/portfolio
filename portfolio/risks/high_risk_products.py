from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from icecream import ic


def high_risk_products(combined_total: float):
    """
    No more 850 in one high risk product.
    """

    sql = """
    select p.product_id, p.descr as product, sum(act.amount) as amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join risk_category risk
    on risk.id = p.risk_category
    where act.status='A'
    and risk.risk_level_descr = 'High'
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    group by p.product_id, p.descr
    having sum(act.amount) > ?
    """
    max_amount = 850
    instances = []
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (max_amount,)).fetchall()

    if rows:
        for row in rows:
            instances.append(
                f"{row.product}. Reduce by {round(row.amount - max_amount)}")

    return instances
