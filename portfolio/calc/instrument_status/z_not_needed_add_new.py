from datetime import datetime
import inspect
import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from portfolio.calc.instrument_status.status_sql import insert_status_sql
from icecream import ic


def add_new(run_id: int):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    current_timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    select_sql = """
    select distinct account_id, product_id, 'OPEN' as instrument_status, 
    ? as effdt, 0 as absence_count, run_id
    from actual_total act
    where not exists
        (select 1 from instrument_status inst
        where inst.account_id=act.account_id 
        and inst.product_id=act.product_id)
    and act.run_id=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(
            select_sql,
            (
                current_timestamp_str,
                run_id,
            ),
        ).fetchall()
        ic(rows)
        if rows:
            c.execute(
                f"{insert_status_sql} {select_sql}",
                (
                    current_timestamp_str,
                    run_id,
                ),
            )
            print(f"Inserted {len(rows)} rows")
