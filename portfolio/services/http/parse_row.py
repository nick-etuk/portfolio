from datetime import datetime
import os
import re
from bs4 import BeautifulSoup
import sqlite3 as sl
from portfolio.calc.changes import change_str
from portfolio.calc.previous.previous_by_seq import previous_by_seq
from portfolio.utils.config import db, output_dir, webdriver, cypress_data_dir
from definitions import root_dir
from portfolio.services.http.find_product import find_product
from portfolio.utils.init import log
from portfolio.utils.lib import (
    named_tuple_factory,
    get_last_seq,
)
from portfolio.utils.utils import first_number


def save_new_total(html, queue_id):
    div = html.find("div", class_=re.compile("HeaderInfo_totalAsset.*"))
    total_text = div.text
    total_text = total_text.replace("$", "").replace(",", "")
    new_total = float(first_number(total_text))

    sql = """
    update html_parse_queue
    set new_total = ?
    where queue_id = ?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(
            sql,
            (new_total, queue_id),
        )

    log(f"HTML total: {round(new_total)} queue_id: {queue_id}")


def parse_row(account_id, run_id, queue_id, timestamp, filename):
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status = "DONE"
    absolute_filename = os.path.join(root_dir, filename)
    if not os.path.exists(absolute_filename):
        log(f"ERROR: {absolute_filename} not found")
        return "ERROR"

    with open(filename) as fp:
        html = BeautifulSoup(fp, "html.parser")

    save_new_total(html, queue_id)

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
        amount = find_product(html, row)
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
            seq, _ = get_last_seq()

            change = ""
            previous = previous_by_seq(
                seq=seq,
                account_id=account_id,
                product_id=row.product_id,
                amount=amount,
                timestamp=timestamp,
            )
            if previous:
                change, _ = change_str(
                    amount=amount,
                    timestamp=timestamp,
                    previous_amount=previous.amount,
                    previous_timestamp=previous.timestamp,
                )

            log(f"{row.product} {round(amount)} {change}")

    return status
