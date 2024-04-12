import inspect
from portfolio.calc.instrument_status.sql import base_select, exec_sql
from icecream import ic


def frequently_missing(run_id: int):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    """
    For each account,
    select all products that it has ever had (first effective date)
    with data source of HTML
    For each of those products
    that is not in the actual_total table for the last run
    and its current status is pending_close

    insert a row into instrument_status with
    absence count=current absence count + 1
    """
    status_filter = "='PENDING_CLOSE'"
    new_status_value = "'PENDING_CLOSE'"
    absence_clause = "inst.absence_count + 1"
    select_sql = base_select(
        status_filter=status_filter,
        absence_clause=absence_clause,
        new_status_value=new_status_value,
        run_id=run_id,
    )
    exec_sql(select_sql)
