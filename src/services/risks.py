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


def rule1():
    combined_total, solomon_total, personal_total, details, table = get_totals(
        "total")
    limit = combined_total * 0.1

    # print(f"More than 10% of total value, {limit}, in one product")

    sql = f"""
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


if __name__ == "__main__":
    #solomon_total, personal_total, details = get_totals("total")
    # log(tabulate(details, headers="firstrow"))
    init()
    rule1()
