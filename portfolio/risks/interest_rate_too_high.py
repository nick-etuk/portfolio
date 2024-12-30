import inspect
from icecream import ic
from portfolio.calc.changes.report_changes import get_account_changes
from portfolio.utils.lib import get_last_run_id


def interest_rate_too_high(combined_total: float):
    """
    APR should not be higher than 20%.
    """
    last_run_id, timestamp = get_last_run_id()
    rows = get_account_changes(last_run_id)
    instances = []
    for row in rows:
        apr = row["apr"]
        change = row["change"]
        if change > 0 and apr > 20:
            instances.append(f"{row['account']} {row['product']} {change}")

    return instances


if __name__ == "__main__":
    ic(interest_rate_too_high(421))
