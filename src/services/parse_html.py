import os
from init import init, log
import sys
import sqlite3 as sl
from config import db, html_dir

from lib import named_tuple_factory
from parse_row import parse_row


def parse_html(run_mode):

    sql = """
        select q.queue_id, q.run_id, q.timestamp, q.account_id, ac.descr as account, q.filename 
        from html_parse_queue q, account ac
        where q.account_id=ac.account_id
        and q.status='PARSING'
        """
    if run_mode == "reload":
        sql = """
            select q.queue_id, q.run_id, q.timestamp, q.account_id, ac.descr as account, q.filename 
            from html_parse_queue q, account ac
            where q.account_id=ac.account_id
            and q.run_id=
                (select max(run_id) from html_parse_queue)
            """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    for row in rows:
        filename = os.path.join(html_dir, row.filename)
        log(f"Parsing {row.account}")
        parse_row(row.account_id, row.run_id, row.timestamp, filename)

        queue_id = row.queue_id
        sql = "update html_parse_queue set status='DONE' where queue_id=?"
        with sl.connect(db) as conn:
            c = conn.cursor()
            c.execute(sql, (queue_id,))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_mode = "normal"
    else:
        run_mode = sys.argv[1]
    init()
    parse_html(run_mode)
