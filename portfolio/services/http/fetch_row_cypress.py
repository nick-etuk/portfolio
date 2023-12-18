from datetime import datetime
import os
import sqlite3 as sl
from portfolio.calc.changes import change_str

from portfolio.utils.config import db, html_dir, html_url, data_dir
from portfolio.utils.lib import named_tuple_factory
from portfolio.utils.init import log
from portfolio.utils.utils import first_number


def fetch_row(param_row, run_id, queue_id, run_mode):
    sql = """
    select act.amount, act.timestamp, ac.descr
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    where act.account_id=?
    and act.product_id=7
    and seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        last_run = c.execute(sql, (param_row.account_id,)).fetchone()

    last_total = last_run.amount

    url = html_url + param_row.address
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d_%H_%M_%S")
    timestamp_str2 = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{param_row.account}_{timestamp_str}"

    cypress_dir = os.path.join(data_dir, "cypress")
    if not os.path.exists(cypress_dir):
        os.mkdir(cypress_dir)

    cypress_file = os.path.join(
        cypress_dir, f"NEW-{param_row.account_id}-{last_run.descr}.csv"
    )
    with open(cypress_file, "w") as f:
        f.write(f"{url},{filename},{last_total}")

    new_total = 0
    status = "PARSING"

    change, apr = change_str(
        amount=new_total,
        timestamp=timestamp_str2,
        previous_amount=last_total,
        previous_timestamp=last_run.timestamp,
    )
    log(f"Status: {status}. New total {round(new_total)}, last total {last_total}")

    sql = """
    update html_parse_queue
    set filename = ?,
    last_total = ?,
    new_total = ?,
    status = ?,
    timestamp = ?
    where queue_id = ?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(
            sql,
            (filename + ".html", last_total, new_total, status, timestamp, queue_id),
        )

    return status
