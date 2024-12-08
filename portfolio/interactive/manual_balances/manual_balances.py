from datetime import datetime
import sqlite3 as sl
from portfolio.interactive.manual_balances.get_account import get_account
from portfolio.utils.config import db
from portfolio.utils.lib import (
    named_tuple_factory,
)
from portfolio.utils.init import init, log
from icecream import ic


def get_manual_balances(run_id, timestamp):
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

    print("Enter manual balances")
    for row in rows:
        print(f"{row.account} {row.address}")
        get_account(row.account_id, run_id, timestamp)


if __name__ == "__main__":
    init()
    get_manual_balances(0, 0)
