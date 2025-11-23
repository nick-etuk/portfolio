
import sys
import sqlite3 as sl
from datetime import datetime
from portfolio.calc.instrument_status.insert_status import insert_status
from portfolio.cli.insert_trade import insert_trade
from portfolio.calc.instrument_status.insert_actual_total import insert_actual_total
from portfolio.services.fetch_data import fetch_data
from portfolio.utils.config import db
from portfolio.utils.init import error, info, init, log, warn
from portfolio.utils.lib import get_last_run_id, named_tuple_factory
from portfolio.cli.match_product_name import match_product_name
from portfolio.utils.next_run_id import get_timestamp, next_run_id
from portfolio.utils.show_usage import show_usage


def process_command():
    action = sys.argv[1].lower()
    args = sys.argv[2:]
    args_len = len(args)

    run_id, _ = get_last_run_id()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    init(run_id)

    if action not in ['fetch', "buy", "sell", "watch"]:
        info(f"Invalid action {action}")
        return
    
    if action == 'fetch':
        args_len = len(sys.argv)
        if args_len == 1:
            run_mode = "normal"
        elif args_len > 1:
            args_list = ["normal", "retry", "reload", "dry_run", "report"]
            if sys.argv[1] not in args_list:
                error(f"Invalid argument: {sys.argv[1]}")
                show_usage()
                sys.exit(1)

            run_mode = sys.argv[1]

        run_id, timestamp = next_run_id(run_mode)
        init(run_id)

        if args_len >= 3:
            run_id = sys.argv[2]
            timestamp = get_timestamp(run_id)

        reload_account = ""
        if args_len == 4:
            reload_account = sys.argv[3]

        if not timestamp:
            warn(f"No timestamp found for {run_id}. Using current timestamp {timestamp}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        fetch_data(run_mode, run_id, timestamp, reload_account)
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