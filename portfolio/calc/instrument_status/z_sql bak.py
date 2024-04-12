import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from icecream import ic

insert_sql = """
insert into instrument_status (account_id, product_id, instrument_status, effdt, 
absence_count, run_id, ac_descr, instrument_descr)

"""


def base_select(
    status_filter: str, absence_clause: str, new_status_value: str, run_id: int
):
    compiled_sql = f"""
    select ac.account_id, prod.product_id, 
    {new_status_value} as instrument_status,
    current_timestamp as effdt,
    {absence_clause} as absence_count,
    {run_id} as run_id,
    ac.descr as ac_descr, prod.descr as instrument_descr
    from product prod
    cross join account ac
    inner join instrument_status inst 
    on inst.product_id=prod.product_id
    and inst.account_id=ac.account_id
    where prod.data_source='HTML'
    and not exists
            (select 1 from actual_total
            where account_id=ac.account_id
            and product_id=prod.product_id
            and run_id={run_id}
            )
    and inst.instrument_status {status_filter}
    """
    print("compiled_sql:")
    print(compiled_sql)
    return compiled_sql


def exec_sql(select_sql: str, insert_sql: str):
    # print(f"{__name__}.{inspect.stack()[0][3]}")
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(select_sql).fetchall()
        ic(rows)
        if rows:
            c.execute(f"{insert_sql} {select_sql}")
            print(f"Inserted {len(rows)} rows")
