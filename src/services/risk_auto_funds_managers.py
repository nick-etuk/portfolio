from lib import named_tuple_factory
import sqlite3 as sl
from config import db
from icecream import ic


def auto_fund_managers(combined_total: float):
    """
    No more than 2 medium security lots in beefy, grizzly or any other automated fund manager.
    i.e max of 6500 * 2 managed by beefy. 
    no more than 40% of total value in one automated fund manager.
    """

    sql = """
    select p.manager, sum(act.amount) as amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    where act.status='A'
    and p.manager <> ' '
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    group by p.manager
    having sum(act.amount) > ?
    """
    # max_amount = combined_total * 0.4
    max_amount = 6500 * 2
    instances = []
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (max_amount,)).fetchall()

    if rows:
        for row in rows:
            instances.append(
                f"{row.manager}. Reduce by {round(row.amount - max_amount)}")

    return instances
