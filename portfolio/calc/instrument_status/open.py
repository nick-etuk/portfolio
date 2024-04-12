import inspect
from portfolio.calc.instrument_status.sql import exec_sql
from icecream import ic


def open(run_id: int):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    # insert into instrument_status (account_id, product_id, instrument_status, effdt, absence_count, run_id)
    select_sql = f"""
    select act.account_id, act.product_id, 'OPEN' as instrument_status, 
    current_timestamp as effdt, 0 as absence_count, act.run_id,
    ac.descr as ac_descr, prod.descr as instrument_descr
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product prod
    on prod.product_id=act.product_id
    where act.seq=(
        select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id={run_id}
        )
    and prod.data_source='HTML'
    and not exists
        (select 1 from instrument_status inst
        where account_id=act.account_id
        and product_id=act.product_id
        and effdt=(
            select max(effdt) from instrument_status
            where account_id=inst.account_id
            and product_id=inst.product_id
            --and run_id={run_id}
            )
        and inst.instrument_status='OPEN'
        )
    and act.run_id={run_id}
    order by act.account_id, act.product_id
    """
    exec_sql(select_sql)
