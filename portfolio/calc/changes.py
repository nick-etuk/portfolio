from datetime import datetime
import inspect
from portfolio.calc.apr import calc_apr
from portfolio.calc.debts_by_product import net_amount
from portfolio.calc.previous.previous_by_run_id import previous_by_run_id
from portfolio.utils.lib import (
    named_tuple_factory,
    get_last_run_id,
)
import sqlite3 as sl
from portfolio.utils.config import db
from dateutil.parser import parse
from icecream import ic
from portfolio.utils.init import init, log

account_col = ""
product_col = ""
amount_col = 0
change_col = ""
table = []


def days_ago(new_timestamp: datetime, old_timestamp: datetime):
    # new_timestamp = parse(new_date)
    # old_timestamp = parse(old_date)
    delta = new_timestamp - old_timestamp
    seconds = delta.total_seconds()
    days = seconds / 60 / 60 / 24

    if days > 365:
        years = days / 365
        label = "year" if round(years) == 1 else "years"
        number_str = "{:.1f}".format(years).strip("0").strip(".")
        result = f"{number_str} {label}"
        return result

    if days > 30:
        months = days / 30
        label = "month" if round(months) == 1 else "months"
        number_str = "{:.0f}".format(months).strip("0").strip(".")
        result = f"{number_str} {label}"
        return result

    if days > 7:
        weeks = days / 7
        label = "week" if round(weeks) == 1 else "weeks"
        number_str = "{:.0f}".format(weeks).strip("0").strip(".")
        result = f"{number_str} {label}"
        return result

    label = "day" if round(days) == 1 else "days"
    number_str = "{:.0f}".format(days).strip("0").strip(".")
    result = f"{number_str} {label}"

    return result


def change_str(amount, timestamp, previous_amount, previous_timestamp):
    if not (previous_amount and previous_timestamp):
        return "New entry", 0

    change = amount - previous_amount
    current_timestamp = parse(timestamp)
    prev_timestamp = parse(previous_timestamp)
    delta = current_timestamp - prev_timestamp
    seconds = delta.total_seconds()
    days = seconds / 60 / 60 / 24

    apr = calc_apr(previous_amount, change, days)

    change_str = ""
    if change != 0:
        change_str = "{:+.0f}".format(change)
        # days_str1 = "day" if round(days) == 1 else "days"
        # days_str2 = "{:.1f}".format(days).strip("0").strip(".")
        # days_str = days_str2 + " " + days_str1
        timespan = days_ago(current_timestamp, prev_timestamp)
        # days_str = f"{days:g} {days_str1}"
        if apr > 0.1:
            # change_str += "  " + "{:.0f}".format(apr) + "%  " + days_str
            change_str = "{:.0f}".format(apr) + "%  " + timespan
        else:
            change_str += "  " + timespan

    return change_str, apr


def get_products(run_id, account_id, account):
    print(
        f"{__name__}.{inspect.stack()[0][3]} run_id: {run_id}, account_id: {account_id}, account: {account}"
    )

    sql = """
    select act.product_id, p.descr as product, p.volatile, act.amount, act.timestamp
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join instrument_status inst
    on inst.account_id=act.account_id
    and inst.product_id=act.product_id
    --and inst.run_id=act.run_id
    where act.run_id = ?
    and act.account_id=?
    and p.subtotal='N'
    and act.status='A'
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id)
    and inst.effdt=(
    select max(effdt) from instrument_status
    where account_id=inst.account_id
    and product_id=inst.product_id
    --and run_id=inst.run_id
    )
    and inst.instrument_status='OPEN'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(
            sql,
            (
                run_id,
                account_id,
            ),
        ).fetchall()

    results = []
    for product in rows:
        amount = net_amount(
            product.amount, account_id=account_id, product_id=product.product_id
        )
        change = ""
        previous = previous_by_run_id(
            run_id=run_id, account_id=account_id, product_id=product.product_id
        )

        if previous:
            change, apr = change_str(
                amount=amount,
                timestamp=product.timestamp,
                previous_amount=previous.amount,
                previous_timestamp=previous.timestamp,
            )

        if change:
            print(account, product.product, amount, change)
            # table.append([account, product.product, amount, change])

            # results.append(                {product.product: {"amount": amount, "change": change, "apr": apr}}            )
            results.append(
                {
                    "account": account,
                    "product": product.product,
                    "amount": amount,
                    "change": change,
                    "apr": apr,
                }
            )
    return results


def get_accounts(run_id):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    sql = """
    select distinct act.run_id, act.account_id, ac.descr as account
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    where act.run_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (run_id,)).fetchall()

    results_array = []
    for account in rows:
        prod_results = get_products(account.run_id, account.account_id, account.account)
        if prod_results:
            results_array += prod_results

    return results_array


def report_changes(run_id: int = 0):
    if not run_id:
        run_id, _ = get_last_run_id()
    result = get_accounts(run_id)
    return result


if __name__ == "__main__":
    init()
    print(report_changes())
