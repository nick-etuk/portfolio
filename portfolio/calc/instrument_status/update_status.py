import sys
from portfolio.calc.instrument_status.open import open
from portfolio.calc.instrument_status.missing_once import missing_once
from portfolio.calc.instrument_status.missing_again import missing_again
from portfolio.calc.instrument_status.closed import closed
from portfolio.calc.instrument_status.report_status_changes import (
    report_instrument_status_changes,
)
from portfolio.utils.lib import get_last_run_id


def update_instrument_status(run_mode: str, run_id: int):
    open(run_mode, run_id)
    missing_once(run_mode, run_id)
    missing_again(run_mode, run_id)
    closed(run_mode, run_id)
    changes = report_instrument_status_changes(run_id)
    return changes


if __name__ == "__main__":
    run_id = get_last_run_id() if len(sys.argv) == 1 else int(sys.argv[1])
    update_instrument_status("dry_run", run_id)
