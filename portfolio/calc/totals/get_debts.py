import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from icecream import ic


def get_debts(borrower_account_id):
    total = 0
    sql = """
    select lo.lender_id, lend.descr as lender, sum(lo.amount) as amount
    from loan lo
    inner join account lend
    on lend.account_id=lo.lender_id
    where lo.borrower_id=?
    and lo.status='A'
    group by lo.lender_id, lend.descr
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (borrower_account_id,)).fetchall()

    results = []
    for loan in rows:
        results.append({"Owed to " + loan.lender: round(loan.amount, 0)})
        total += loan.amount

    return total, results
