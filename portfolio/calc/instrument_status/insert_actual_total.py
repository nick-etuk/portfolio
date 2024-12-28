import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import (
    named_tuple_factory,
)
from portfolio.utils.init import log
from portfolio.utils.next_seq import get_next_seq


def insert_actual_total(
    run_id, timestamp, account_id, product_id, amount, units=0, price=0, status="A"
):
    next_seq = get_next_seq()
    insert_sql = """
    insert into actual_total (seq, account_id, product_id, run_id, timestamp, amount, units, price, status, dummy)
    values(?,?,?,?,?,?,?,?,?,?)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(
            insert_sql,
            (
                next_seq,
                account_id,
                product_id,
                run_id,
                timestamp,
                round(amount),
                units,
                price,
                status,
                "N",
            ),
        )
        conn.commit()
