from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from icecream import ic


def get_details(product_id: int):
    sql = """
    select ac.account_id, ac.descr as account, p.descr as product, p.chain, act.amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join account ac
    on ac.account_id=act.account_id
    inner join instrument_status inst
    on inst.account_id=act.account_id
    and inst.product_id=act.product_id
    where act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and inst.effdt=(
        select max(effdt) from instrument_status
        where account_id=inst.account_id
        and product_id=inst.product_id
    )
    and inst.instrument_status='OPEN'
    and act.product_id = ?
    and act.status='A'
    """
    details = ""
    total = 0

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (product_id,)).fetchall()

    for row in rows:
        details += f"""
        <tr>
            <td>{row.account}</td>
            <td>{row.product}</td>
            <td>{row.chain}</td>
            <td>{row.amount}</td>
        </tr>
        """
        total += row.amount

    return details, total


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
    inner join instrument_status inst
    on inst.account_id=act.account_id
    and inst.product_id=act.product_id
    where 1=1
    and p.subtotal='N'
    and p.cash='N'
    and act.status='A'
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and inst.effdt=(
        select max(effdt) from instrument_status
        where account_id=inst.account_id
        and product_id=inst.product_id
    )
    and inst.instrument_status='OPEN'
    group by p.product_id, p.descr
    having sum(act.amount) > ?
    """
    # max_amount = combined_total * 0.1
    max_amount = 6500
    instances = []
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (max_amount,)).fetchall()

    if not rows:
        return instances

    for row in rows:
        detail_header = f"""
        <p>{row.product}. Reduce by {round(row.amount - max_amount)}</p>
        <table>
            <tr>
                <td>Account</td>
                <td>Product</td>
                <td>Chain</td>
                <td>Amount</td>
            </tr>
        """
        detail_rows, detail_total = get_details(row.product_id)

        detail_footer = f"""
        <tr>
            <td></td>
            <td></td>
            <td>Total</td>
            <td>{detail_total}</td>
        </tr>
        </table>
        """

        instances.append(detail_header + detail_rows + detail_footer)

    return instances

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
    """


if __name__ == "__main__":
    print(medium_risk_products(0000))
