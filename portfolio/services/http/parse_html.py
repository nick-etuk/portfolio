import os
from portfolio.utils.init import init, log
import sys
import sqlite3 as sl
from portfolio.utils.config import db, output_dir, webdriver, cypress_data_dir

from portfolio.utils.lib import named_tuple_factory
from portfolio.services.http.parse_row import parse_row


def parse_html(run_mode):
    sql = """
        select q.queue_id, q.run_id, q.timestamp, q.account_id, ac.descr as account, q.filename 
        from html_parse_queue q, account ac
        where q.account_id=ac.account_id
        and q.status='PARSING'
        """
    if run_mode in ["reload", "retry"]:
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
        raw_html_dir = (
            os.path.join(cypress_data_dir, "output-html", str(row.run_id))
            if webdriver == "cypress"
            else output_dir
        )
        filename = os.path.join(raw_html_dir, row.filename)
        log(f"Parsing {row.account}")
        status = parse_row(
            row.account_id, row.run_id, row.queue_id, row.timestamp, filename
        )

        queue_id = row.queue_id
        sql = "update html_parse_queue set status=? where queue_id=?"
        with sl.connect(db) as conn:
            c = conn.cursor()
            c.execute(
                sql,
                (
                    status,
                    queue_id,
                ),
            )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_mode = "normal"
    else:
        run_mode = sys.argv[1]
    init()
    parse_html(run_mode)
