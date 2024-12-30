from portfolio.calc.previous.previous_by_seq import previous_by_seq
from portfolio.calc.previous.previous_by_timestamp import get_prevous_by_timestamp
from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from icecream import ic
from portfolio.utils.init import init
from dateutil.parser import parse


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
    order by act.account_id, act.product_id
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    for row in rows:
        current_amount = row.amount
        current_timestamp = row.timestamp
        # formatted_timestamp = current_timestamp.strftime("%Y-%m-%d %H")
        previous = previous_by_seq(
            seq=row.seq,
            account_id=row.account_id,
            product_id=row.product_id,
            amount=current_amount,
            timestamp=current_timestamp,
        )

        while previous:
            formatted_timestamp = parse(current_timestamp).strftime("%Y-%m-%d %H")
            if previous.amount != current_amount:
                print(
                    f"{formatted_timestamp} {row.account} {row.product} new:{current_amount} old:{previous.amount} change:{previous.change}"
                )
                current_amount = previous.amount
            previous = previous_by_seq(
                seq=previous.seq,
                account_id=row.account_id,
                product_id=row.product_id,
                amount=current_amount,
                timestamp=current_timestamp,
            )
            if previous:
                current_timestamp = previous.timestamp

    """
    accounts_result = {}
    for account in rows:
        products_result = {}
        result = get_products(account.run_id, account.account_id)
        if result:
            products_result[account.account] = result

    accounts_result = {run_id: products_result}

    return accounts_result
    """


def interest_rate_history():
    get_account_product()


if __name__ == "__main__":
    init()
    interest_rate_history()
