from datetime import datetime
import os
from bs4 import BeautifulSoup
import sqlite3 as sl
from portfolio.calc.changes import change_str
from portfolio.utils.config import db, output_dir, webdriver, cypress_data_dir
from definitions import root_dir
from portfolio.services.http.find_product import find_product
from portfolio.utils.init import log
from portfolio.utils.lib import (
    named_tuple_factory,
    previous_values_by_seq,
    get_last_seq,
)


def parse_row(account_id, run_id, timestamp, filename):
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status = "DONE"
    # convert relative path to absolute path
    absolute_filename = os.path.join(root_dir, filename)
    if not os.path.exists(absolute_filename):
        log(f"ERROR: {absolute_filename} not found")
        return "ERROR"

    with open(filename) as fp:
        html = BeautifulSoup(fp, "html.parser")

    sql = """
    select product_id, descr as product, chain, project, html_label, html_table_columns
    from product
    where data_source='HTML'
    """

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    for row in rows:
        amount = find_product(
            html=html,
            prod_descr=row.product,
            chain=row.chain,
            project=row.project,
            prod_label=row.html_label,
            html_table_coloumns=row.html_table_columns,
        )
        if amount:
            sql = """
            insert into actual_total (product_id, account_id, run_id, timestamp, amount, status)
            values(?,?,?,?,?,?)
            """
            with sl.connect(db) as conn:
                conn.row_factory = named_tuple_factory
                c = conn.cursor()
                c.execute(
                    sql,
                    (
                        row.product_id,
                        account_id,
                        run_id,
                        timestamp,
                        amount,
                        "A",
                    ),
                )
            seq, discard_me = get_last_seq()

            change = ""
            previous = previous_values_by_seq(
                seq=seq, account_id=account_id, product_id=row.product_id
            )
            if previous:
                change, apr = change_str(
                    amount=amount,
                    timestamp=timestamp,
                    previous_amount=previous.amount,
                    previous_timestamp=previous.timestamp,
                )

            log(f"{row.product} {round(amount)} {change}")

    return status
