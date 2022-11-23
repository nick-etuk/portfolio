from lib import named_tuple_factory
import sqlite3 as sl
from config import db
from init import log
from dateutil.parser import parse
from icecream import ic
from tabulate import tabulate
from init import init, log
from totals import get_totals
import pandas as pd


def auto_fund_managers(combined_total: float):
    """
    No more than 2 medium security lots in beefy, grizzly or any other automated fund manager.
    i.e max of 6500 * 2 managed by beefy. 
    no more than 40% of total value in one automated fund manager.
    """

    sql = """
    select p.manager, sum(act.amount) as amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    where act.status='A'
    and p.manager <> ' '
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    group by p.manager
    having sum(act.amount) > ?
    """
    # max_amount = combined_total * 0.4
    max_amount = 6500 * 2
    instances = []
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (max_amount,)).fetchall()

    if rows:
        for row in rows:
            instances.append(
                f"{row.manager}. Reduce by {round(row.amount - max_amount)}")

    return instances


def rule1():
    combined_total, solomon_total, personal_total, details, table = get_totals(
        "total")
    limit = combined_total * 0.1

    # print(f"More than 10% of total value, {limit}, in one product")

    sql = """
    select act.account_id, ac.descr as account, act.product_id, p.descr as product, sum(act.amount) as amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join account ac
    on ac.account_id=act.account_id
    where 1=1
    and p.subtotal='N'
    and p.cash='N'
    and act.status='A'
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    group by act.account_id, ac.descr, act.product_id, p.descr
    """
    with sl.connect(db) as conn:
        df = pd.read_sql_query(sql, conn)

    print(df)
    df_original = df[['product', 'amount']].groupby('product').sum()

    print(f"More than 10% of total value, {limit}, in one product")
    df = df_original[(df_original.amount > limit)]
    print(df)

    total_cash, solomon_cash, personal_cash, details, table = get_totals(
        "cash")
    if total_cash > 0:
        print(f"Room left to invest {total_cash} in these products:")
        under_subscribed = df_original[(df_original.amount < limit)]
        df = under_subscribed.apply(lambda x: limit - x)
        print(df)


def check_risks():
    rules = [
        {
            'rule_id': 2,
            'descr': r"No more than 40% of total value with one fund manager.",
            'function': auto_fund_managers

        }
    ]

    combined_total, solomon_total, personal_total, details, table = get_totals(
        "total")

    result = []
    for rule in rules:
        instances = rule['function'](combined_total)
    if instances:
        result.append({**rule, 'instances': instances})

    return to_html(result) if result else ''


def to_html(violations):
    output = f"<h2 style='color:red'>Risk Violations</h2>"
    for violation in violations:
        output += f"<h2>{violation['descr']}</h2>"
        for instance in violation['instances']:
            output += f"<p>{instance}</p>"

    return output


if __name__ == "__main__":
    #solomon_total, personal_total, details = get_totals("total")
    # log(tabulate(details, headers="firstrow"))
    init()
    print(check_risks())
    # print(auto_fund_managers(60000))
