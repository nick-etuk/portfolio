import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from icecream import ic


def get_assets(lender_account_id, lender_account):
    total = 0
    sql = """
    select lo.borrower_id, bo.descr as borrower, sum(lo.amount) as amount
    from loan lo
    inner join account bo
    on bo.account_id=lo.borrower_id
    where lo.lender_id=?
    and lo.status='A'
    group by lo.borrower_id, bo.descr
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (lender_account_id,)).fetchall()

    results = []
    result_table = []

    for loan in rows:
        results.append({"Loan to " + loan.borrower: round(loan.amount, 0)})
        total += loan.amount
        result_table.append(
            [
                lender_account,
                "Loan to " + loan.borrower,
                round(loan.amount, 0),
                "",
                "",
                "",
            ]
        )

    return total, results, result_table
