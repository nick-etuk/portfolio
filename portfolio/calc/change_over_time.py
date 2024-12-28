from portfolio.calc.changes import change_str
from portfolio.calc.previous.first_entry import first_entry
from portfolio.calc.previous.previous_by_days_elapsed import previous_by_days_elapsed
from portfolio.calc.previous.previous_by_run_id import previous_by_run_id


class Changes:
    def __init__(self, last_run: str, weekly: str, monthly: str, alltime: str):
        self.last_run = last_run
        self.weekly = weekly
        self.monthly = monthly
        self.alltime = alltime


def get_change_overtime(run_id, account_id, product_id, amount, timestamp) -> Changes:
    last_run_change = ""
    previous = previous_by_run_id(
        run_id=run_id, account_id=account_id, product_id=product_id
    )
    if previous:
        last_run_change, _ = change_str(
            amount=amount,
            timestamp=timestamp,
            previous_amount=previous.amount,
            previous_timestamp=previous.timestamp,
        )

    weekly_change = ""
    previous = previous_by_days_elapsed(
        account_id=account_id, product_id=product_id, days=7
    )
    if previous:
        weekly_change, _ = change_str(
            amount=amount,
            timestamp=timestamp,
            previous_amount=previous.amount,
            previous_timestamp=previous.timestamp,
        )

    monthly_change = ""
    previous = previous_by_days_elapsed(
        account_id=account_id, product_id=product_id, days=30
    )
    if not previous:
        previous = first_entry(account_id=account_id, product_id=product_id)
    if previous:
        monthly_change, _ = change_str(
            amount=amount,
            timestamp=timestamp,
            previous_amount=previous.amount,
            previous_timestamp=previous.timestamp,
        )

    alltime_change = ""
    previous = first_entry(account_id=account_id, product_id=product_id)
    if previous:
        alltime_change, _ = change_str(
            amount=amount,
            timestamp=timestamp,
            previous_amount=previous.amount,
            previous_timestamp=previous.timestamp,
        )

    return Changes(
        last_run=last_run_change,
        weekly=weekly_change,
        monthly=monthly_change,
        alltime=alltime_change,
    )
