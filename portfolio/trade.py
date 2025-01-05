
import sys
import sqlite3 as sl
from portfolio.calc.instrument_status.insert_status import insert_status
from portfolio.calc.instrument_status.insert_trade import insert_trade
from portfolio.calc.instrument_status.insert_actual_total import insert_actual_total
from portfolio.utils.config import db
from portfolio.utils.init import info
from portfolio.utils.lib import get_last_run_id, named_tuple_factory
from portfolio.trades.find_trade_product import find_trade_product


def make_trade():
    if len(sys.argv) < 3:
        info("Usage: trade.py <buy|sell> <product>")
        return
    
    action = sys.argv[1].lower()
    args = sys.argv[2:]

    if action not in ["buy", "sell"]:
        info(f"Invalid action {action}")
        return
    
    prod = find_trade_product(args)
    if not prod:
        return
    
    sql = """
    select act.amount, act.units, act.price,
    ac.account_id, ac.descr as account
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    where act.product_id=?
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (prod["product_id"],)).fetchall()

    if not rows:
        info(f"Not currently holding {prod['product']}")
        return
    
    if len(rows) > 1:
        info(f"Multiple accounts holding {prod['product']}:")
        for row in rows:
            info(f"{row.account_id} {row.account}")
        return
    
    info(f"{action.capitalize()}ing {rows[0].account} {prod['product']} {rows[0].amount}")

    account_id = rows[0].account_id
    amount = rows[0].amount

    run_id, timestamp = get_last_run_id()

    insert_actual_total(
        run_id=run_id,
        timestamp=timestamp,
        account_id=account_id,
        product_id=prod["product_id"],
        amount=amount,
        units=rows[0].units,
        price=rows[0].price,
        status="I",
    )

    insert_status(
        account_id=account_id,
        product_id=prod["product_id"],
        status="CLOSED",
        run_id=run_id,
    )

    if action == "sell":
        amount = -amount

    insert_trade(action, account_id, prod["product_id"], amount)


if __name__ == "__main__":
    make_trade()