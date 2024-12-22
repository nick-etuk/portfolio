from datetime import datetime
import sqlite3 as sl
import inspect
from portfolio.calc.changes import change_str
from portfolio.calc.previous.previous_by_run_id import previous_by_run_id
from portfolio.utils.config import db
from portfolio.utils.lib import (
    get_last_run_id,
    named_tuple_factory,
)
from portfolio.utils.init import init, log, info

# from changes import change_str, get_last_run_id
# from portfolio.services.api.ftx import ftx_balance
from portfolio.services.api.binance import binance_balance
from portfolio.services.api.moralis.defi_balances import moralis_defi_balance
from portfolio.services.api.coin_market_cap import cmc_get_value
from icecream import ic


def fetch_api(run_id, timestamp):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    if not timestamp:
        log("Fetch API: No timestamp, using current date and time")
        timestamp = datetime.now().isoformat()

    sql = """
        select ac.account_id, ac.address, ac.descr as account,
        act.dummy, 
        p.product_id, p.descr as product, p.data_source
        from actual_total act
        inner join account ac
        on ac.account_id=act.account_id
        inner join product p
        on p.product_id=act.product_id
        where act.seq=
            (select max(seq) from actual_total
            where account_id=act.account_id
            and product_id=act.product_id
            )
        /* and p.data_source in ('CMC', 'MORALIS_API', 'BINANCE_API') */
        and p.data_source in ('CMC', 'MORALIS_API')
        and act.status='A'
        """
    api = {
        "BINANCE_API": binance_balance,
        "CMC": cmc_get_value,
        "MORALIS_API": moralis_defi_balance,
    }

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    for row in rows:
        info(f"{row.data_source} {row.account} {row.product}")
        try:
            result = api[row.data_source](
                account_id=row.account_id,
                product_id=row.product_id,
                product=row.product,
            )
            if result:
                insert_sql = """
                insert into actual_total (product_id, account_id, run_id, timestamp, amount, units, price, status, dummy)
                values(?,?,?,?,?,?,?,?,?)
                """
                with sl.connect(db) as conn:
                    conn.row_factory = named_tuple_factory
                    c = conn.cursor()
                    c.execute(
                        insert_sql,
                        (
                            row.product_id,
                            row.account_id,
                            run_id,
                            timestamp,
                            result["value"],
                            result["units"],
                            result["price"],
                            "A",
                            row.dummy,
                        ),
                    )

                # seq, discard_me = get_last_seq()

                previous = previous_by_run_id(
                    run_id=run_id,
                    account_id=row.account_id,
                    product_id=row.product_id,
                )

                change = ""
                if previous:
                    change, _ = change_str(
                        amount=result["value"],
                        timestamp=timestamp,
                        previous_amount=previous.amount,
                        previous_timestamp=previous.timestamp,
                    )

            log(
                f"{row.data_source} {row.account} {row.product}: {round(result['value'])}  {change}"
            )
        except Exception as e:
            msg = f"{e}"
            # print(msg)
            log(msg[:130])
            print(
                f"Error row: {row.data_source}, {row.account}, {row.product}, {round(result['value'])}"
            )


if __name__ == "__main__":
    init()
    run_id, timestamp = get_last_run_id()
    print(f"last run_id, timestamp: {run_id}, {timestamp}")
    fetch_api(run_id, timestamp)
