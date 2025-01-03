import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory

def current_actual(account_id: int, product_id: int):
    sql = """
    select act.run_id, act.account_id, ac.descr as account, prod.product_id, prod.descr as product, act.amount, act.units, act.price
    from actual_total act
    inner join product prod
    on prod.product_id=act.product_id
    inner join account ac
    on ac.account_id=act.account_id
    where act.seq=(
        select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
    )
    and act.account_id=?
    and act.product_id=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (account_id, product_id)).fetchone()

    return row