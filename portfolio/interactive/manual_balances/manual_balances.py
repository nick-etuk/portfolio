from datetime import datetime
import sqlite3 as sl
from portfolio.interactive.manual_balances.get_manual_balance import get_manual_balance
from portfolio.utils.config import db
from portfolio.utils.lib import (
    named_tuple_factory,
)
from portfolio.utils.init import info, init, log
from icecream import ic


def get_manual_balances(run_id, timestamp):
    print("Please check Defi Lama before proceeding.")
    input("Press Enter to continue:")
    
    if not timestamp:
        timestamp = datetime.now().isoformat()

    account_sql = """
    select ac.account_id, ac.descr as account, ac.address
    from account ac
    where ac.address <> ''
    """

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(account_sql).fetchall()

    info("Enter manual balances")
    for row in rows:
        get_manual_balance(row.account_id, run_id, timestamp)


if __name__ == "__main__":
    init()
    get_manual_balances(0, 0)
