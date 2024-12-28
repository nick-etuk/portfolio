import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory


def get_next_seq():
    sql = """
    select max(seq) as max_seq
    from actual_total
    """

    max_seq = 0
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql).fetchone()

    if row:
        max_seq = row.max_seq

    return max_seq + 1
