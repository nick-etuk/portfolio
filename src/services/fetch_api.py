import sqlite3 as sl
from config import db
from lib import get_last_seq, named_tuple_factory, previous_values_by_run_id
from init import init, log
from changes import change_str, get_last_run_id
from fetch_ftx import ftx_balance
from fetch_binance import binance_balance
from fetch_coin_market_cap import cmc_get_value
from icecream import ic


def fetch_api(run_id, timestamp):
    sql = """
        select act.account_id, act.dummy, ac.descr as account, 
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
        and p.data_source in ('FTX_API', 'BINANCE_API', 'CMC')
        and act.status='A'
        """
    api = {'FTX_API': ftx_balance,
           'BINANCE_API': binance_balance,
           'CMC': cmc_get_value}

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

        for row in rows:
            try:
                result = api[row.data_source](
                    row.account_id, row.product_id, row.product)
                if result:
                    sql = """
                    insert into actual_total (product_id, account_id, run_id, timestamp, amount, units, price, status, dummy)
                    values(?,?,?,?,?,?,?,?,?)
                    """
                    with sl.connect(db) as conn:
                        conn.row_factory = named_tuple_factory
                        c = conn.cursor()
                        c.execute(sql, (row.product_id, row.account_id,
                                  run_id, timestamp, result['value'], result['units'], result['price'], 'A', row.dummy))

                    # seq, discard_me = get_last_seq()

                    previous = previous_values_by_run_id(run_id=run_id,
                                                         account_id=row.account_id, product_id=row.product_id)

                    change = ''
                    if previous:
                        change, apr = change_str(amount=result['value'], timestamp=timestamp,
                                                 previous_amount=previous.amount, previous_timestamp=previous.timestamp)

                log(
                    f"{row.data_source} {row.account} {row.product}: {round(result['value'])}  {change}")
            except Exception as e:
                msg = f"{e}"
                print(msg)
                log(msg[:130])


if __name__ == "__main__":
    init()
    run_id, timestamp = get_last_run_id()
    fetch_api(run_id, timestamp)
