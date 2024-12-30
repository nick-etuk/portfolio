import inspect
from portfolio.calc.instrument_status.sql import (
    base_select,
    insert_status_rows,
)
from icecream import ic


def closed(run_mode: str, run_id: int):
    """
    For each account/product combination
    that is not in the actual_total table for the last run
    and its current instrument status is pending_close
    and the absence count is greater than 4

    insert a row into instrument_status with
    status of closed
    """
    status_filter = "='PENDING_CLOSE'"
    new_status_value = "'CLOSED'"
    absence_column = "1"
    general_filter = "and inst.absence_count > 4"
    sql = base_select(
        status_filter=status_filter,
        absence_column=absence_column,
        new_status_value=new_status_value,
        run_id=run_id,
        general_filter=general_filter,
    )
    insert_status_rows(sql=sql, run_mode=run_mode, run_id=run_id, status="CLOSED")
