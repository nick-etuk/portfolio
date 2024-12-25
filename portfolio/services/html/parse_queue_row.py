from datetime import datetime
import os
import re
import sys
from bs4 import BeautifulSoup
from portfolio.calc.changes import change_str
from portfolio.calc.previous.previous_by_seq import previous_by_seq
from portfolio.utils.config import db
from definitions import root_dir
from portfolio.services.html.find_product import find_product
from portfolio.utils.init import info, init, log
import sqlite3 as sl
from portfolio.utils.lib import (
    named_tuple_factory,
    get_last_seq,
)
from portfolio.utils.utils import first_number
from icecream import ic


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

    info(f"HTML total {round(new_total)}")


def parse_queue_row(
    account_id, run_id, queue_id, timestamp, filename, absolute_filename=None
):
    # ic(account_id, run_id, queue_id, timestamp, filename)
    # if account_id != 1:        return "DONE"
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not absolute_filename:
        absolute_filename = os.path.join(root_dir, filename)
        if not os.path.exists(absolute_filename):
            log(f"ERROR: {absolute_filename} not found")
            return "ERROR"

    status = "DONE"

    with open(absolute_filename, "r") as fp:
        html = BeautifulSoup(fp, "html.parser")

    save_new_total(html, queue_id)

    product_sql = """
    select p.product_id, p.descr as product, p.chain, 
    p.project, p.html_label, p.html_table_columns
    from product p
    where p.data_source='HTML'
    """

    account_sql = """
    select ac.descr as account, ac.address
    from account ac
    where ac.account_id=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        account_row = c.execute(account_sql, (account_id,)).fetchone()

    old_sql = """
    select p.product_id, p.descr as product, p.chain, 
    p.project, p.html_label, p.html_table_columns,
    act.amount as old_amount, 
    ac.descr as account, ac.address
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join account ac
    on ac.account_id=act.account_id
    where act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        )
    and ac.account_id=?
    and act.status='A'
    and p.data_source='HTML'
    """

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        product_rows = c.execute(product_sql).fetchall()

    for product_row in product_rows:
        amount = find_product(
            html=html,
            row=product_row,
            account_id=account_id,
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
                        product_row.product_id,
                        account_id,
                        run_id,
                        timestamp,
                        round(amount),
                        "A",
                    ),
                )
            seq, _ = get_last_seq()

            change = ""
            previous = previous_by_seq(
                seq=seq,
                account_id=account_id,
                product_id=product_row.product_id,
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

            if change:
                info(
                    f"HTML {account_row.account} {product_row.product} {round(amount)} change [{change}]"
                )
            else:
                info(
                    f"HTML {account_row.account} {product_row.product} {round(amount)}"
                )

    return status


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_mode = "normal"
    else:
        run_mode = sys.argv[1]
    init()
    parse_queue_row(
        account_id=2,
        run_id=411,
        queue_id=1586,
        timestamp=None,
        filename="Solomon High_2024-05-25_09_10_03.html",
        absolute_filename=None,
    )
