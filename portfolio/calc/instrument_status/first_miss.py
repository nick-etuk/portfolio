import inspect
from portfolio.calc.instrument_status.sql import base_select, exec_sql
from icecream import ic


def first_time_missing(run_id: int):
    print(f"{__name__}.{inspect.stack()[0][3]}")
    """
    For each account,
    select all products that it has ever had (first effective date)
    with data source of HTML
    For each of those products
    if it is not in the actual_total table for the last run
    and its current instrument status is OPEN or CLOSED
    then insert a row into instrument_status with
    absence count=1, status=PENDING_CLOSE, run_id=current run_id
    """
    status_filter = "in ('OPEN', 'CLOSED')"
    new_status_value = "'PENDING_CLOSE'"
    absence_clause = "1"
    select_sql = base_select(
        status_filter=status_filter,
        absence_clause=absence_clause,
        new_status_value=new_status_value,
        run_id=run_id,
    )
    exec_sql(select_sql)
