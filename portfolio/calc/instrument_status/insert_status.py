import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory

from portfolio.calc.instrument_status.status_sql import insert_status_sql


def insert_status(account_id, product_id, status, run_id, absence_count=0):
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(insert_status_sql, (
            account_id,
            product_id,
            status,
            absence_count,
            run_id))
        conn.commit()