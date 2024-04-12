import sys
from portfolio.calc.instrument_status.open import open
from portfolio.calc.instrument_status.first_miss import first_time_missing
from portfolio.calc.instrument_status.frequently_missing import frequently_missing
from portfolio.calc.instrument_status.closed import closed
from portfolio.calc.instrument_status.report_changes import (
    report_instrument_status_changes,
)
from portfolio.utils.lib import get_last_run_id


def update_instrument_status(run_id: int):
    open(run_id)
    first_time_missing(run_id)
    frequently_missing(run_id)
    closed(run_id)
    changes = report_instrument_status_changes(run_id)
    return changes


if __name__ == "__main__":
    run_id = get_last_run_id() if len(sys.argv) == 1 else int(sys.argv[1])
    update_instrument_status(run_id)
