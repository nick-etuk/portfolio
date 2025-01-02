import inspect
import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from portfolio.calc.instrument_status.sql import insert_status_sql
from icecream import ic


def final_miss(run_id: int):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    """
    For each account/web product combination
    that is not in the actual_total table for the last run
    and its current instrument status is pending_close
    and the absence count is greater than 4

    insert a row into instrument_status with
    status of closed
    """

    select_sql = """
    select ac.account_id, prod.product_id, 
    'CLOSED' as instument_status,
    current_datetime as effdt
    inst.absence_count + 1 as absence_count
    from product prod
    cross join account ac
    inner join instrument inst 
    on inst.product_id=prod.product_id
    and inst.account_id=ac.account_id
    where prod.data_source='HTML'
    and not exists
            (select 1 from actual_total
            where account_id=ac.account_id
            and product_id=prod.product_id
            and run_id=?
            )
    and inst.instrument_status='PENDING_CLOSE'
    and inst.absence_count > 4
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(select_sql, (run_id,)).fetchall()
        ic(rows)
        if rows:
            c.execute(f"{insert_status_sql} {select_sql}", (run_id,))
            print(f"Inserted {len(rows)} rows")
