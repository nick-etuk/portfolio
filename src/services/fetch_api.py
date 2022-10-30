import sqlite3 as sl
from config import db
from lib import get_last_seq, named_tuple_factory, previous_values_by_run_id
from init import init, log
from changes import change_str, get_last_run_id
from fetch_ftx import ftx_balance
from fetch_binance import binance_balance


def fetch_api(run_id, timestamp):
    sql = """
        select act.account_id, ac.descr as account, 
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
        and act.status='A'
        """
    api = {'FTX_API': ftx_balance,
           'BINANCE_API': binance_balance}

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

        for row in rows:
            if row.data_source not in ['FTX_API', 'BINANCE_API']:
                continue

            try:
                amount = api[row.data_source](row.account_id, row.product)
                if amount:
                    sql = """
                    insert into actual_total (product_id, account_id, run_id, timestamp, amount, status)
                    values(?,?,?,?,?,?)
                    """
                    with sl.connect(db) as conn:
                        conn.row_factory = named_tuple_factory
                        c = conn.cursor()
                        c.execute(sql, (row.product_id, row.account_id,
                                        run_id, timestamp, amount, 'A',))

                    seq, discard_me = get_last_seq()

                    previous = previous_values_by_run_id(run_id=run_id,
                                                         account_id=row.account_id, product_id=row.product_id)

                    change = change_str(amount=amount, timestamp=timestamp,
                                        previous_amount=previous.amount, previous_timestamp=previous.timestamp)

                log(f"{row.data_source} {row.account} {row.product}: {round(amount)}")
            except Exception as e:
                msg = f"{e}"
                print(msg)
                log(msg[:130])


if __name__ == "__main__":
    init()
    run_id, timestamp = get_last_run_id()
    fetch_api(run_id, timestamp)
