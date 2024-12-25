import os
import inspect
from portfolio.utils.init import init, log, info, warn, error
import sys
import sqlite3 as sl
from portfolio.utils.config import db, output_dir, webdriver, cypress_data_dir

from portfolio.utils.lib import named_tuple_factory
from portfolio.services.html.parse_queue_row import parse_queue_row


def parse_html(run_mode: str, run_id: int = 0, reload_account: int = None):
    print(f"{__name__}.{inspect.stack()[0][3]}")
    sql = """
        select q.queue_id, q.run_id, q.timestamp, q.account_id, ac.descr as account, q.filename 
        from html_parse_queue q, account ac
        where q.account_id=ac.account_id
        and ac.address <> ' '
        and q.status='PARSING'
        """
    args = ()

    if run_mode == "reload":
        """
        Reload with an argument: Parse the given run_id.
        Reload with no argumnents: Parse the last run_id
        """
        sql = """
            select q.queue_id, q.run_id, q.timestamp, q.account_id, ac.descr as account, q.filename 
            from html_parse_queue q, account ac
            where q.account_id=ac.account_id
            and ac.address <> ' '
            """

        if run_id:
            sql += f"\n and q.run_id={run_id}"
        else:
            sql += "\n and q.run_id=(select max(run_id) from html_parse_queue)"

        if reload_account:
            sql += "\n and q.account_id=?"
            args = (reload_account,)

    if run_mode == "retry":
        """
        Retry: Try again to parse failed runs
        """
        sql = """
            select q.queue_id, q.run_id, q.timestamp, q.account_id, ac.descr as account, q.filename 
            from html_parse_queue q, account ac
            where q.account_id=ac.account_id
            and ac.address <> ' '
            and q.status not in ('DONE','PARSING')
            and q.run_id=
                (select max(run_id) from html_parse_queue)
            """

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, args).fetchall()

    for row in rows:
        raw_html_dir = (
            os.path.join(cypress_data_dir, "output-html", str(row.run_id))
            if webdriver == "cypress"
            else output_dir
        )
        filename = os.path.join(raw_html_dir, row.filename)
        info(f"Parsing {row.filename}")
        status = parse_queue_row(
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
    # parse_html(run_mode)
    parse_html("reload")
