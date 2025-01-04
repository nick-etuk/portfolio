from portfolio.calc.totals.get_totals import get_totals
from portfolio.utils.init import init, log
from portfolio.utils.lib import get_last_run_id
from portfolio.utils.next_run_id import get_timestamp
from icecream import ic


def show_totals(run_id, timestamp, totals_mode):
    # total, solomon_total, personal_total, _, result_table = get_totals(totals_mode)
    totals = get_totals(run_id=run_id, timestamp=timestamp, totals_mode=totals_mode)
    log(f"Solomon {totals_mode}: {totals.solomon}")
    log(f"Personal {totals_mode}: {totals.personal}")
    log(f"Combined {totals_mode}: {totals.combined}")
    return totals


if __name__ == "__main__":
    init()
    # run_id = 415
    run_id, _ = get_last_run_id()
    result = show_totals(
        run_id=run_id, timestamp=get_timestamp(run_id), totals_mode="total"
    )
    # show_totals("cash")
