import inspect
from portfolio.calc.instrument_status.sql import base_select, insert_status_rows
from icecream import ic

from portfolio.utils.lib import get_last_run_id


def missing(run_mode: str, run_id: int):
    """
    For each account,
    select all products that are open or pending close
    in instrument_status, but not in actual_total
    for the last run
    """
    sql = """
    select inst.account_id, inst.product_id, inst.effdt,
    'PENDING_CLOSE' as status, absence_count,
    ac.descr as account, p.descr as product
    from instrument_status inst
    inner join account ac
    on ac.account_id=inst.account_id
    inner join product p
    on p.product_id=inst.product_id
    where inst.effdt=(
        select max(effdt) from instrument_status
        where account_id=inst.account_id
        and product_id=inst.product_id
    )
    and p.data_source not in ('MANUAL')
    and p.subtotal='N'
    and inst.instrument_status in ('OPEN', 'PENDING_CLOSE')
    and not exists (
        select 1 from actual_total act
        where act.seq=(
            select max(seq) from actual_total
            where account_id=act.account_id
            and product_id=act.product_id
            and run_id=act.run_id
            )
        and act.account_id=inst.account_id
        and act.product_id=inst.product_id
        and act.run_id=?
    )
    order by inst.account_id, inst.product_id
    """
    insert_status_rows(
        sql=sql, run_mode=run_mode, run_id=run_id, status="PENDING_CLOSE"
    )

if __name__ == "__main__":
    run_id, _ = get_last_run_id()
    missing("dry_run", run_id)