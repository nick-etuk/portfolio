import sqlite3 as sl
from portfolio.calc.changes import change_str
from portfolio.calc.instrument_status.insert_actual_total import insert_actual_total
from portfolio.calc.previous.previous_by_run_id import previous_by_run_id
from portfolio.utils.config import db
from portfolio.utils.lib import (
    named_tuple_factory,
)
from portfolio.utils.init import log


def get_manual_balance(account_id, run_id, timestamp):
    product_sql = """
    select p.product_id, p.descr as product, act.amount,
    ac.descr as account, ac.address
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product p
    on p.product_id=act.product_id
    where act.account_id=?
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        )
    and act.status='A'
    and p.data_source in ('MANUAL')
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(product_sql, (account_id,)).fetchall()

    for row in rows:
        print(f"{row.account} {row.address}")
        amount = input(f"{row.product} ({row.amount}):")
        if not amount:
            continue

        insert_actual_total(
            run_id=run_id,
            timestamp=timestamp,
            account_id=account_id,
            product_id=row.product_id,
            amount=amount,
        )

        previous = previous_by_run_id(
            run_id=run_id,
            account_id=account_id,
            product_id=row.product_id,
        )

        change = ""
        if previous:
            change, _ = change_str(
                amount=float(amount),
                timestamp=timestamp,
                previous_amount=previous.amount,
                previous_timestamp=previous.timestamp,
            )

        log(f"change: {change}")
