import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory


def get_debts_by_product(account_id):
    sql = """
    select lo.borrower_product_id as product_id, sum(lo.amount) as amount
    from loan lo
    where lo.borrower_id=?
    and lo.status='A'
    group by lo.borrower_product_id
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (account_id,)).fetchall()

    result = {}
    for row in rows:
        result[row.product_id] = row.amount

    return result


def net_amount(amount, account_id, product_id):
    debts = get_debts_by_product(account_id)
    if product_id in debts:
        amount -= debts[product_id]
    return amount
