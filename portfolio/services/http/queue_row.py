from datetime import datetime
import os
import sqlite3 as sl
from portfolio.calc.changes import change_str

from portfolio.utils.config import db, output_dir, html_url, data_dir
from portfolio.utils.lib import named_tuple_factory
from portfolio.utils.init import log
from portfolio.utils.utils import first_number


def queue_row(param_row, run_id, queue_id, run_mode):
    sql = """
    select act.amount, act.timestamp, ac.descr
    from account ac 
    left outer join actual_total act
    on ac.account_id=act.account_id
    where ac.account_id=?
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

    last_total = last_run.amount if last_run else 0

    url = html_url + param_row.address
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d_%H_%M_%S")
    timestamp_str2 = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{param_row.account}_{timestamp_str}.html"

    # log(f"URL {url}, filename {filename}, last total {last_total}")
    return url, filename, last_total, timestamp
