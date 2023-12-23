import json
import os
import sys

import sqlite3 as sl
from icecream import ic
from portfolio.services.queue.queue_row import queue_row

from portfolio.utils.init import log
from portfolio.utils.lib import max_queue_id, named_tuple_factory
from portfolio.utils.config import db, cypress_data_dir


def queue_html_accounts(run_id, run_mode):
    sql = """
        select ac.account_id, ac.descr as account, ac.address 
        from account ac
        where ac.address <> ' '
        """
    args = ()

    if run_mode == "reload":
        sql = """
        select q.queue_id, ac.account_id, ac.descr as account, ac.address 
        from account ac
        where ac.address <> ' '
        """
        args = ()

        if len(sys.argv) == 3:
            sql = """
            select q.queue_id, ac.account_id, ac.descr as account, ac.address 
            from account ac
            where ac.address <> ' '
            and account_id=?
            """
            account_id = sys.argv[2]
            args = (account_id,)

    if run_mode == "retry":
        sql = """
        select q.queue_id, ac.account_id, ac.descr as account, ac.address, q.status
        from account ac
        inner join html_parse_queue q
        on q.account_id=ac.account_id
        where ac.address <> ' '
        and q.status not in ('DONE','PARSING')
        and q.timestamp > date('now','-1 day')
        """
        args = ()

    accounts_array = []

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, args).fetchall()

    for row in rows:
        log(f"Queuing {row.account}")

        if run_mode != "normal":
            queue_id = row.queue_id
        else:
            sql = """
            insert into html_parse_queue (run_id, account_id, filename, last_total, new_total, status, timestamp)
            values (?,?,?,?,?,?,?)
            """
            with sl.connect(db) as conn:
                conn.row_factory = named_tuple_factory
                c = conn.cursor()
                c.execute(sql, (run_id, row.account_id, " ", 0, 0, "FETCHING", None))
            queue_id = max_queue_id()

        url, filename, last_total, timestamp = queue_row(row)
        accounts_array.append(
            {
                "queueId": queue_id,
                "url": url,
                "fileName": filename,
                "lastTotal": last_total,
                "timestamp": timestamp,
            }
        )

    cypress_queue_file = os.path.join(
        cypress_data_dir, "queue", f"cypressQueue-{run_id}.json"
    )
    with open(cypress_queue_file, "a") as f:
        f.write(json.dumps(accounts_array, indent=4))

    return "PARSING"
