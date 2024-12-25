import inspect
from portfolio.calc.instrument_status.sql import insert_status_rows
from icecream import ic
from portfolio.utils.init import info


def open(run_mode: str, run_id: int):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    sql = """
    select act.account_id, act.product_id, act.timestamp as effdt,
    ac.descr as account, prod.descr as product
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product prod
    on prod.product_id=act.product_id
    where act.seq=(
        select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id
        )
    -- and prod.data_source='HTML'
    and not exists
        (select 1 from instrument_status inst
        where account_id=act.account_id
        and product_id=act.product_id
        and effdt=(
            select max(effdt) from instrument_status
            where account_id=inst.account_id
            and product_id=inst.product_id
            )
        and inst.instrument_status='OPEN'
        )
    and act.run_id=?
    order by act.account_id, act.product_id
    """
    insert_status_rows(sql=sql, run_mode=run_mode, run_id=run_id, status="OPEN")
