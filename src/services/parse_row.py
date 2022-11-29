from datetime import datetime, date
import os
from bs4 import BeautifulSoup
import sqlite3 as sl
from config import db, html_dir
from find_product import find_product
from init import log
from lib import named_tuple_factory, previous_values_by_seq, get_last_seq
from changes import change_str


def parse_row(account_id, run_id, timestamp, filename):
    html_file = os.path.join(html_dir, filename)
    with open(html_file) as fp:
        html = BeautifulSoup(fp, 'html.parser')

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
        amount = find_product(html=html, prod_descr=row.product,
                              chain=row.chain, project=row.project, prod_label=row.html_label, html_table_coloumns=row.html_table_columns)
        if amount:
            sql = """
            insert into actual_total (product_id, account_id, run_id, timestamp, amount, status)
            values(?,?,?,?,?,?)
            """
            with sl.connect(db) as conn:
                conn.row_factory = named_tuple_factory
                c = conn.cursor()
                c.execute(sql, (row.product_id, account_id,
                                run_id, timestamp, amount, 'A',))
            seq, discard_me = get_last_seq()

            change = ''
            previous = previous_values_by_seq(
                seq=seq, account_id=account_id, product_id=row.product_id)
            if previous:
                change, apr = change_str(amount=amount, timestamp=timestamp,
                                         previous_amount=previous.amount, previous_timestamp=previous.timestamp)

            log(f"{row.product} {round(amount)} {change}")
