
import sys
import sqlite3 as sl
from portfolio.calc.instrument_status.insert_status import insert_status
from portfolio.cli.insert_trade import insert_trade
from portfolio.calc.instrument_status.insert_actual_total import insert_actual_total
from portfolio.services.fetch_data import fetch_data
from portfolio.utils.config import db
from portfolio.utils.init import info
from portfolio.utils.lib import get_last_run_id, named_tuple_factory
from portfolio.cli.match_product_name import match_product_name


def process_command():
    if len(sys.argv) < 3:
        info("Usage: trade.py <buy|sell> <product>")
        return
    
    action = sys.argv[1].lower()
    args = sys.argv[2:]

    if action not in ['fetch', "buy", "sell", "watch"]:
        info(f"Invalid action {action}")
        return
    
    if action == 'fetch':
        fetch_data()
        return
    
    product = match_product_name(args)
    if not product:
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
        rows = c.execute(sql, (product["product_id"],)).fetchall()

    if not rows:
        info(f"Not currently holding {product['product']}")
        return
    
    if len(rows) > 1:
        info(f"Multiple accounts holding {product['product']}:")
        for row in rows:
            info(f"{row.account_id} {row.account}")
        return
    
    info(f"{action.capitalize()}ing {rows[0].account} {product['product']} {rows[0].amount}")
    input("Press Enter to confirm or ctrl-c to cancel: ")
    return

    account_id = rows[0].account_id
    amount = rows[0].amount

    run_id, timestamp = get_last_run_id()

    insert_actual_total(
        run_id=run_id,
        timestamp=timestamp,
        account_id=account_id,
        product_id=product["product_id"],
        amount=amount,
        units=rows[0].units,
        price=rows[0].price,
        status="I",
    )

    insert_status(
        account_id=account_id,
        product_id=product["product_id"],
        status="CLOSED",
        run_id=run_id,
    )

    if action == "sell":
        amount = -amount

    insert_trade(action, account_id, product["product_id"], amount)


if __name__ == "__main__":
    process_command()