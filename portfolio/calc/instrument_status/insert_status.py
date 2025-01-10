import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory

insert_status_sql = """
insert into instrument_status (account_id, product_id, effdt, instrument_status, absence_count, run_id)
values (?, ?, current_timestamp, ?, ?, ?)
"""

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