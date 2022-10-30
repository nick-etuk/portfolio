from bs4 import BeautifulSoup
from lib import named_tuple_factory, calc_apr, previous_values_by_run_id, get_last_run_id
import sqlite3 as sl
from config import db
from dateutil.parser import parse
from icecream import ic
from init import init, log
from datetime import datetime


def change_str(amount, timestamp, previous_amount, previous_timestamp):
    change = amount - previous_amount
    current_timestamp = parse(timestamp)
    prev_timestamp = parse(previous_timestamp)
    delta = current_timestamp - prev_timestamp
    seconds = delta.total_seconds()
    days = seconds/60/60/24

    apr = calc_apr(previous_amount, change, days)

    change_str = ""
    if change != 0:
        change_str = "{:+.0f}".format(change)
        days_str1 = "day" if round(days, 1) == 1.0 else "days"
        days_str2 = "{:.1f}".format(days).strip("0").strip(".")
        days_str = days_str2 + " " + days_str1
        # days_str = f"{days:g} {days_str1}"
        if apr > 0.1:
            change_str += "  " + "{:.0f}".format(apr) + "%  " + days_str

    return change_str


def get_products(run_id, account_id):
    sql = """
    select act.product_id, p.descr as product, p.volatile, act.amount, act.timestamp
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    where run_id = ?
    and account_id=?
    and p.subtotal='N'
    and act.status='A'
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (run_id, account_id,)).fetchall()

    results = []
    for product in rows:
        change = ""
        previous = previous_values_by_run_id(
            run_id=run_id, account_id=account_id, product_id=product.product_id)

        if previous:
            change = change_str(amount=product.amount, timestamp=product.timestamp,
                                previous_amount=previous.amount, previous_timestamp=previous.timestamp)

        if change:
            results.append(
                {
                    product.product:
                    {
                        "amount": product.amount,
                        "change": change
                    }
                }
            )

    return results


def get_accounts(run_id):
    sql = """
    select act.run_id, act.account_id, ac.descr as account
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    where run_id=?
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and run_id=act.run_id)
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (run_id,)).fetchall()

    accounts_result = {}
    products_result = {}
    for account in rows:
        result = get_products(account.run_id, account.account_id)
        if result:
            products_result[account.account] = result

    accounts_result = {run_id: products_result}

    return accounts_result


def report_changes(run_id: int = 0):
    if not run_id:
        run_id, timestamp = get_last_run_id()
    result = get_accounts(run_id)
    ic(result)


if __name__ == "__main__":
    init()
    report_changes()
    # print(round(0.97, 1))
    # print(round(0.97, 2))
