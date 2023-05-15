from portfolio.utils.init import log
from bs4 import BeautifulSoup
import re
from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from dateutil.parser import parse
from icecream import ic
from changes import get_last_run_id, change_str


def previous_high(current):
    sql = """
    select seq, max(amount) as amount
    from actual_total act
    where  account_id=?
    and product_id=?
    and act.status='A'
    group by seq
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(
            sql, (current.account_id, current.product_id,)).fetchone()

    return row


def unexpected_falls():
    run_id, timestamp = get_last_run_id()
    sql = """
    select act.seq, act.account_id, ac.descr as account, p.product_id, p.descr as product, act.amount
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product p
    on p.product_id=act.product_id
    where seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and p.volatile='N'
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    for current in rows:
        prev_high = previous_high(current)
        change = prev_high.amount - current.amount
        if change > 0:
            summary = "Unexpected fall"
            details = f"Unexpected fall of ${change} on #{current.seq} in {current.account} {current.product} to {current.amount}. Prevous high of {prev_high.amount} on #{prev_high.seq}"
            log(summary, details, current.seq)

    return


def current_values(run_id):
    sql = """
    select act.run_id, act.account_id, act.product_id, act.timestamp, act.amount,
    ac.descr as account, p.descr as product
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product p
    on p.product_id=act.product_id
    where run_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (run_id,)).fetchall()

    for current in rows:
        previous = previous_high(current)
        # ic(current.run_id, previous.run_id)
        old_value = previous.amount
        change = current.amount - old_value
        current_timestamp = parse(current.timestamp)
        previous_timestamp = parse(previous.timestamp)
        delta = current_timestamp - previous_timestamp
        seconds = delta.total_seconds()
        days = seconds/60/60/24

        # ic(current_timestamp, previous_timestamp, days, seconds)
        apr = change/old_value/365*days/100
        change_str = "{:+.0f}".format(change)
        if apr > 0.1:
            change_str += " (" + "{:.1f}".format(apr) + "%)"
        if change != 0:
            log(
                f"{current.account} {current.product} {change_str}")


if __name__ == "__main__":
    unexpected_falls()
