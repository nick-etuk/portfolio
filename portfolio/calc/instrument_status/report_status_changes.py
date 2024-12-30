import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from icecream import ic


def report_instrument_status_changes(run_id: int):
    sql = """
    select ac.descr as account, prod.descr as instrument, 
    act.amount,
    inst.instrument_status, inst.absence_count
    from instrument_status inst
    inner join product prod
	on prod.product_id=inst.product_id
    inner join account ac
	on ac.account_id=inst.account_id
    inner join actual_total act
    on act.account_id=inst.account_id
    and act.product_id=inst.product_id
    where act.seq=(
        select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id
    )
    and act.run_id=inst.run_id
    and inst.run_id=?
    order by ac.account_id, prod.product_id
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (run_id,)).fetchall()

    # if rows:
    #     simple = tabulate(
    #         rows,
    #         tablefmt="simple",
    #         headers=["account", "instrument", "value", "status", "absence_count"],
    #     )
    #     # print(simple)
    return rows
