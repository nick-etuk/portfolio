import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from tabulate import tabulate
from portfolio.utils.init import info, log
from icecream import ic

insert_sql = """
insert into instrument_status (account_id, product_id, effdt, instrument_status, absence_count, run_id, ac_descr, instrument_descr)
values (?, ?, ?, ?, ?, ?, ?, ?)
"""


def base_select(
    status_filter: str,
    absence_column: str,
    new_status_value: str,
    run_id: int,
    general_filter: str = "",
):
    compiled_sql = f"""
    select ac.account_id, prod.product_id, 
    {new_status_value} as instrument_status,
    current_timestamp as effdt,
    {absence_column} as absence_count,
    {run_id} as run_id,
    ac.descr as account, prod.descr as product
    from actual_total act
    inner join product prod
	on prod.product_id=act.product_id
    inner join account ac
	on ac.account_id=act.account_id
    inner join instrument_status inst 
    on inst.product_id=prod.product_id
    and inst.account_id=ac.account_id
    where act.seq=(
		select max(seq) from actual_total
		where account_id=act.account_id
		and product_id=act.product_id
	)
    and not exists
            (select 1 from actual_total
            where account_id=act.account_id
            and product_id=act.product_id
            )
    and inst.effdt=(
        select max(effdt) from instrument_status
        where account_id=inst.account_id
        and product_id=inst.product_id
        )
    and inst.instrument_status {status_filter}
    {general_filter}
    and act.run_id=?
    order by ac.account_id, prod.product_id
    """
    return compiled_sql


def insert_status_rows(sql: str, run_mode: str, run_id: int, status: str):

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (run_id,)).fetchall()

    for row in rows:
        if status == "PENDING_CLOSE":
            info(
                f"{row.account} {row.product} will be closed in  {4-absence_count} runs"
            )
            absence_count = row.absence_count + 1
        else:
            info(f"{row.account} {row.product} is {status}")
            absence_count = 0

        if run_mode == "dry_run":
            continue

        with sl.connect(db) as conn:
            conn.row_factory = named_tuple_factory
            c = conn.cursor()
            c.execute(
                insert_sql,
                (
                    # account_id, product_id, effdt, instrument_status, absence_count, run_id, ac_descr, instrument_descr
                    row.account_id,
                    row.product_id,
                    row.effdt,
                    status,
                    absence_count,
                    run_id,
                    row.account,
                    row.product,
                ),
            )
            conn.commit()
