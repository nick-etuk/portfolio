import inspect
from portfolio.calc.instrument_status.sql import insert_status_rows
from icecream import ic
from portfolio.utils.init import info


def retrospecive_close(run_mode: str, run_id: int):
    # print(f"{__name__}.{inspect.stack()[0][3]}")

    sql = """
    select act.seq, act.run_id, ac.descr as account, prod.descr as product,
    act.amount, act.timestamp,
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    inner join product prod
    on prod.product_id=act.product_id
    inner join instrument_status inst
    on inst.account_id=act.account_id
    and inst.product_id=act.product_id
    where act.seq=(
        select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and inst.effdt=(
        select max(effdt) from instrument_status
        where account_id=inst.account_id
        and product_id=inst.product_id)
    and act.status='A'
    and inst.instrument_status='CLOSED'
    --order by act.account_id, act.product_id
    """
    insert_status_rows(sql=sql, run_mode=run_mode, run_id=run_id, status="OPEN")
