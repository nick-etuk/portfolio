import inspect
from portfolio.calc.instrument_status.sql import base_select, exec_sql
from icecream import ic


def closed(run_id: int):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    """
    For each account/web product combination
    that is not in the actual_total table for the last run
    and its current instrument status is pending_close
    and the absence count is greater than 4

    insert a row into instrument_status with
    status of closed
    """
    status_filter = "='PENDING_CLOSE'"
    new_status_value = "'CLOSED'"
    absence_clause = "1"
    post_fix = "and inst.absence_count > 4"
    select_sql = base_select(
        status_filter=status_filter,
        absence_clause=absence_clause,
        new_status_value=new_status_value,
        run_id=run_id,
        post_fix=post_fix,
    )
    exec_sql(select_sql)
