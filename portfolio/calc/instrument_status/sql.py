import sqlite3 as sl

from tabulate import tabulate
from portfolio.utils.config import db
from portfolio.utils.init import log
from portfolio.utils.lib import named_tuple_factory
from icecream import ic

insert_sql = """
insert into instrument_status (account_id, product_id, instrument_status, effdt, 
absence_count, run_id, ac_descr, instrument_descr)

"""


def base_select(
    status_filter: str,
    absence_clause: str,
    new_status_value: str,
    run_id: int,
    post_fix: str = "",
):
    compiled_sql = f"""
    select ac.account_id, prod.product_id, 
    {new_status_value} as instrument_status,
    current_timestamp as effdt,
    {absence_clause} as absence_count,
    {run_id} as run_id,
    ac.descr as ac_descr, prod.descr as instrument_descr
    from actual_total act
    inner join product prod
	on prod.product_id=act.product_id
    inner join account ac
	on ac.account_id=act.account_id
    inner join instrument_status inst 
    on inst.product_id=prod.product_id
    and inst.account_id=ac.account_id
    where prod.data_source='HTML'
	and act.seq=(
		select max(seq) from actual_total
		where account_id=act.account_id
		and product_id=act.product_id
	)
    and not exists
            (select 1 from actual_total
            where account_id=act.account_id
            and product_id=act.product_id
            --and run_id={run_id}
            )
    and inst.effdt=(
    select max(effdt) from instrument_status
    where account_id=inst.account_id
    and product_id=inst.product_id
    and run_id={run_id}
    )
    and inst.instrument_status {status_filter}
    {post_fix}
    order by ac.account_id, prod.product_id
    """
    # print(compiled_sql)
    return compiled_sql


def exec_sql(select_sql: str):
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(select_sql).fetchall()
        if rows:
            c.execute(f"{insert_sql} {select_sql}")
            log(f"Inserted {len(rows)} rows")

            rows_output = tabulate(
                rows,
                tablefmt="simple",
                headers=[
                    "account_id",
                    "product_id",
                    "instrument_status",
                    "effdt",
                    "absence_count",
                    "run_id",
                    "ac_descr",
                    "instrument_descr",
                ],
            )
            #     print(rows_output)
