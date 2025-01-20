from datetime import datetime
import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.init import log, warn
from portfolio.utils.lib import named_tuple_factory


def next_run_id(run_mode):
    if run_mode == "dry_run":
        return 0, None

    sql = """
    select run_id, timestamp from actual_total
    where run_id=(select max(run_id) from actual_total)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql).fetchone()

    run_id = row.run_id
    timestamp = row.timestamp
    if run_mode == "normal":
        run_id += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return run_id, timestamp


def get_timestamp(run_id):
    sql = """
    select min(timestamp) as timestamp 
    from actual_total
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
