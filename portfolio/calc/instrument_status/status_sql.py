import sqlite3 as sl
from portfolio.calc.instrument_status.current_actual import current_actual
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from portfolio.calc.changes.days_ago import plural
from portfolio.calc.instrument_status.insert_actual_total import insert_actual_total
from tabulate import tabulate
from portfolio.utils.init import info, log
from icecream import ic


insert_status_sql = """
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
    act.amount, act.units, act.price,
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
            absence_count = int(row.absence_count)

            if absence_count >= 4:
                info(
                    f"{row.account} {row.product} has been missing {absence_count} times. It will be closed."
                )
                status = "CLOSED"
            else:
                absence_count += 1
                info(
                    f"{row.account} {row.product} will be closed in {plural(5-absence_count, 'run')}"
                )
            
        else:
            info(f"{row.account} {row.product} is {status}")
            absence_count = 0

        if run_mode in ["dry_run", "report"]:
            continue

        with sl.connect(db) as conn:
            conn.row_factory = named_tuple_factory
            c = conn.cursor()
            c.execute(
                insert_status_sql,
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

        if status == "CLOSED":
            current_act = current_actual(row.account_id, row.product_id)
            insert_actual_total(
                run_id=run_id,
                timestamp=row.effdt,
                account_id=row.account_id,
                product_id=row.product_id,
                amount=current_act.amount,
                units=current_act.units,
                price=current_act.price,
                status="I",
            )
