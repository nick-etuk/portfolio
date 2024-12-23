import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory


def next_run_id(run_mode):
    sql = """
    select run_id, timestamp from html_parse_queue
    where run_id=(select max(run_id) from html_parse_queue)
    """
    # print("db:", db)
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql).fetchone()

    run_id = row.run_id
    if run_mode == "normal":
        run_id += 1
    return run_id, row.timestamp
