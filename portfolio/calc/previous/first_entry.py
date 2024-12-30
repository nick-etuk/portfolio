import sqlite3 as sl
from portfolio.calc.debts_by_product import net_amount
from portfolio.utils.config import db
from portfolio.utils.dict_to_object import AttrDict
from portfolio.utils.init import warn
from portfolio.utils.lib import named_tuple_factory


def first_entry(account_id: int, product_id: int):
    sql = """
    select seq, run_id, timestamp, amount
    from actual_total act
    where seq=
        (select min(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and account_id=?
    and product_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql,(account_id, product_id)).fetchone()

    if not row:
        warn("No first record for {account_id}, {product_id}")
        return None

    # amount = net_amount(row.amount, account_id, product_id)
    return AttrDict(
        {
            "seq": row.seq,
            "run_id": row.run_id,
            "timestamp": row.timestamp,
            "amount": row.amount,
        }
    )
