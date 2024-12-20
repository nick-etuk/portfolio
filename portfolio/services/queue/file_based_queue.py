import json
import os
import sys
import inspect
import sqlite3 as sl
from icecream import ic
from portfolio.services.queue.queue_row import queue_row

from portfolio.utils.init import log
from portfolio.utils.lib import max_queue_id, named_tuple_factory
from portfolio.utils.config import db, cypress_data_dir


def queue_html_accounts(run_id: int, run_mode: str, reload_account: int = None):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    sql = """
        select ac.account_id, ac.descr as account, ac.address 
        from account ac
        where ac.address <> ' '
        """
    args = ()

    if run_mode == "reload":
        # reload accounts regardless of status
        sql = """
        select q.queue_id, ac.account_id, ac.descr as account, ac.address, q.status
        from account ac
        inner join html_parse_queue q
        on q.account_id=ac.account_id
        where ac.address <> ' '
        and q.run_id=?
        """
        args = (run_id,)

        if reload_account:
            # reload a specific account
            sql = """
            select q.queue_id, ac.account_id, ac.descr as account, ac.address, q.status
            from account ac
            inner join html_parse_queue q
            on q.account_id=ac.account_id
            where ac.address <> ' '
            and q.run_id=?
            and ac.account_id=?
            """
            args = (
                run_id,
                reload_account,
            )

    if run_mode == "retry":
        # reload only accounts that have not been parsed
        # in the last 24 hours
        sql = """
        select q.queue_id, ac.account_id, ac.descr as account, ac.address, q.status
        from account ac
        inner join html_parse_queue q
        on q.account_id=ac.account_id
        where ac.address <> ' '
        and q.status not in ('DONE','PARSING')
        and q.run_id=?
        """
        # and q.timestamp > date('now','-1 day')
        args = (run_id,)

    accounts_array = []
    # ic(run_mode, run_id, reload_account)
    # print(sql)
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, args).fetchall()

    cypress_queue_file = os.path.join(
        cypress_data_dir, "queue", f"cypressQueue-{run_id}.json"
    )
    for row in rows:
        if run_mode != "normal":
            queue_id = row.queue_id
        else:
            log(f"Queuing {row.account}")
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

    # if run_mode == "normal":
    with open(cypress_queue_file, "w") as f:
        f.write(json.dumps(accounts_array, indent=4))

    return "PARSING"
