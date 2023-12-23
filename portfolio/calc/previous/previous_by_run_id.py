import sqlite3 as sl
from portfolio.calc.debts_by_product import net_amount
from portfolio.utils.config import db
from portfolio.utils.dict_to_object import AttrDict
from portfolio.utils.lib import named_tuple_factory


def previous_by_run_id(run_id, account_id, product_id):
    sql = """
    select run_id, timestamp, amount
    from actual_total act
    where run_id=
        (select max(run_id) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id<?)
    and seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id)
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
                run_id,
                account_id,
                product_id,
            ),
        ).fetchone()
    if not row:
        return row

    # amount = net_amount(row.amount, account_id, product_id)
    return AttrDict(
        {"run_id": row.run_id, "timestamp": row.timestamp, "amount": row.amount}
    )
