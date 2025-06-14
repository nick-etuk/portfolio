import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory


def insert_initial_buys():
    insert_sql = """
    insert into trade (date, type, account_id, product_id, amount_usd, dummy)
    select act.timestamp, 'BUY', act.account_id, act.product_id, act.amount, act.dummy
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    where act.seq=
        (select min(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and exists
        (select 1 from actual_total x
        where x.account_id=act.account_id
        and x.product_id=act.product_id
        and x.seq=(select max(seq) from actual_total
            where account_id=x.account_id
            and product_id=x.product_id)
        and x.status='A'
        )
    and p.subtotal='N'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(insert_sql)
        conn.commit()

if __name__ == "__main__":
    insert_initial_buys()
