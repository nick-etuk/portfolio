import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.dict_to_object import AttrDict
from portfolio.utils.lib import named_tuple_factory


def previous_by_days_elapsed(account_id: int, product_id: int, days: float):
    sql = """
    select seq, run_id, timestamp, amount
    from actual_total act
    where seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and timestamp < date('now',?))
    and account_id=?
    and product_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(
            sql,
            (
                f"-{days-1} days",
                account_id,
                product_id,
            ),
        ).fetchone()

    if not row:
        return row

    # amount = net_amount(row.amount, account_id, product_id)
    return AttrDict(
        {
            "seq": row.seq,
            "run_id": row.run_id,
            "timestamp": row.timestamp,
            "amount": row.amount,
        }
    )
