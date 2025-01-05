import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory


def insert_trade(action, account_id, product_id, amount):
    insert_sql = """
    insert into trade (date, type, account_id, product_id, amount_usd)
    values(current_timestamp, ?,?,?,?)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(insert_sql,
            (
                action.upper(),
                account_id,
                product_id,
                amount
            ))
        conn.commit()
