from bs4 import BeautifulSoup
import re
from lib import named_tuple_factory
from lib import calc_apr
import sqlite3 as sl
from config import db
from dateutil.parser import parse
from icecream import ic
from init import init, log


def get_last_run_id():
    sql = """
    select max(run_id) as run_id from actual_total
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql).fetchone()
    return row.run_id


def previous_values(current):
    sql = """
    select run_id, timestamp, amount
    from actual_total act
    where run_id=
        (select max(run_id) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id<?)
    and seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id)
    and account_id=?
    and product_id=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (current.run_id, current.account_id,
                        current.product_id,)).fetchone()

    return row


def amounts(account, product):
    sql = """
    select act.run_id, act.account_id, act.product_id, act.timestamp, act.amount
    from actual_total act
    where run_id=?
    and account_id=?
    and product_id=?
    and seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(
            sql, (account.run_id, account.account_id, product.product_id)).fetchall()

    for current in rows:
        result = {}
        previous = previous_values(current)
        # ic(current.run_id, previous.run_id)
        old_value = previous.amount
        change = current.amount - old_value
        current_timestamp = parse(current.timestamp)
        previous_timestamp = parse(previous.timestamp)
        delta = current_timestamp - previous_timestamp
        seconds = delta.total_seconds()
        days = seconds/60/60/24

        # ic(current_timestamp, previous_timestamp, days, seconds)
        apr = calc_apr(old_value, change, days)
        change_str = ""
        if change != 0:
            change_str = "{:+.0f}".format(change)
            if apr > 0.1:
                change_str += "  " + "{:.1f}".format(apr) + "%"

            result = {"amount": current.amount,
                      "change": change_str
                      }

    # ic(result)
    return result


def products(account):
    sql = """
    select act.product_id, p.descr as product, p.volatile
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    where run_id = ?
    and account_id=?
    and p.subtotal='N'
    and seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (account.run_id, account.account_id,)).fetchall()

    results = []
    for product in rows:
        result = amounts(account, product)
        if result:
            results.append({product.product: result})

    return results


def report_changes():
    run_id = get_last_run_id()
    sql = """
    select act.run_id, act.account_id, ac.descr as account
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product p
    on p.product_id=act.product_id
    where run_id=?
    and p.subtotal='N'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (run_id,)).fetchall()

    results = {}
    for account in rows:
        result = products(account)
        results[account.account] = result

    result = {run_id: results}
    ic(result)
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
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (run_id,)).fetchall()

    for current in rows:
        previous = previous_values(current)
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
    init()
    report_changes()
