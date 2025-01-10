import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory


def net_trades(as_of_date, account_id, product_id):
    sql = """
    select sum(amount_usd) as amount
    from trade
    where account_id=?
    and product_id=?
    and date<=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql,(account_id, product_id, as_of_date)).fetchone()

    return row.amount if row and row.amount else 0

if __name__ == "__main__":
    print("Before sale:", net_trades("2023-03-09", 1, 10))
    print("After sale:", net_trades("2025-01-08", 1, 10))
