
from portfolio.calculations.changes import change_str
from portfolio.utils.lib import named_tuple_factory, previous_values_days_ago
import sqlite3 as sl
from portfolio.utils.config import db
from dateutil.parser import parse
from icecream import ic
from portfolio.utils.init import init, log


def get_prevous_by_timestamp(current_seq, account_id, account, product_id, product, current_amount, current_timestamp):
    sql = """
    select seq, timestamp, amount
    from actual_total act
    where account_id=?
    and product_id=?
    and timestamp=
        (select max(timestamp) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and timestamp < ?)
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        previous = c.execute(sql, (account_id,
                                   product_id, current_timestamp)).fetchone()

    if not previous:
        return

    change, apr = change_str(amount=current_amount, timestamp=current_timestamp,
                             previous_amount=previous.amount, previous_timestamp=previous.timestamp)

    if change:
        timestamp = parse(current_timestamp)
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H")

        print(f"{formatted_timestamp} {account} {product} {current_amount} {change}")

    get_prevous_by_timestamp(current_seq=previous.seq, account_id=account_id, account=account, product_id=product_id,
                             product=product, current_amount=previous.amount, current_timestamp=previous.timestamp)


def get_account_product():
    sql = """
    select act.seq, act.account_id, ac.descr as account, 
    act.product_id, p.descr as product, act.amount,
    act.timestamp
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product p
    on p.product_id=act.product_id
    where act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and p.subtotal='N'
    and p.volatile='N'
    and act.status='A'
    /* order by act.seq */
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    for row in rows:
        get_prevous_by_timestamp(current_seq=row.seq, account_id=row.account_id, account=row.account,
                                 product_id=row.product_id, product=row.product, current_amount=row.amount, current_timestamp=row.timestamp)

    '''
    accounts_result = {}
    for account in rows:
        products_result = {}
        result = get_products(account.run_id, account.account_id)
        if result:
            products_result[account.account] = result

    accounts_result = {run_id: products_result}

    return accounts_result
    '''


def interest_rate_history():
    get_account_product()


if __name__ == "__main__":
    init()
    interest_rate_history()
