from datetime import datetime
import sqlite3 as sl

from portfolio.utils.config import db, output_dir, html_url, data_dir
from portfolio.utils.lib import named_tuple_factory


def queue_row(param_row):
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
    filename = f"{param_row.account}_{timestamp_str}.html"
    timestamp_str2 = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # log(f"URL {url}, filename {filename}, last total {last_total}")
    return url, filename, last_total, timestamp_str2
