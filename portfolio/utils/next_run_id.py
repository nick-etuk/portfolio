import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.init import log, warn
from portfolio.utils.lib import named_tuple_factory


def next_run_id(run_mode):
    if run_mode == "dry_run":
        return 0, None

    sql = """
    select run_id, timestamp from html_parse_queue
    where run_id=(select max(run_id) from html_parse_queue)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql).fetchone()

    run_id = row.run_id
    if run_mode == "normal":
        run_id += 1

    return run_id, row.timestamp


def get_timestamp(run_id):
    sql = """
    select min(timestamp) as timestamp 
    from html_parse_queue
    where run_id=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (run_id,)).fetchone()

    if not row:
        warn(f"No timestamp found for {run_id}")
        return None

    return row.timestamp
