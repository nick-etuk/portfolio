import inspect
from portfolio.calc.instrument_status.status_sql import base_select, insert_status_rows
from icecream import ic


def z_missing_once(run_mode: str, run_id: int):
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
    absence_column = "1"
    sql = base_select(
        status_filter=status_filter,
        absence_column=absence_column,
        new_status_value=new_status_value,
        run_id=run_id,
    )
    insert_status_rows(
        sql=sql, run_mode=run_mode, run_id=run_id, status="PENDING_CLOSE"
    )
