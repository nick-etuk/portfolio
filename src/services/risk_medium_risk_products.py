from lib import named_tuple_factory
import sqlite3 as sl
from config import db
from icecream import ic


def medium_risk_products(combined_total: float):
    """
    No more than 10% in any one product, regardless of risk
    """

    sql = """
    select p.product_id, p.descr as product, sum(act.amount) as amount
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
    group by p.product_id, p.descr
    having sum(act.amount) > ?
    """
    #max_amount = combined_total * 0.1
    max_amount = 6500
    instances = []
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (max_amount,)).fetchall()

    if rows:
        for row in rows:
            instances.append(
                f"{row.product}. Reduce by {round(row.amount - max_amount)}")

    return instances

    '''
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
    '''
