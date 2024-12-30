from dateutil.parser import parse

from portfolio.calc.changes.apr import calc_apr
from portfolio.calc.changes.change_classes import Change, Changes
from portfolio.calc.previous.first_entry import first_entry
from portfolio.calc.previous.previous_by_days_elapsed import previous_by_days_elapsed
from portfolio.calc.previous.previous_by_run_id import previous_by_run_id
from portfolio.utils.init import init, warn
from icecream import ic

from portfolio.utils.lib import get_last_run_id


def get_change_overtime(run_id, account_id, product_id, amount, timestamp_str) -> Changes:
    last_run_change_str = ""
    weekly_change_str= ""
    monthly_change_str = ""
    alltime_change_str = ""
    timestamp = parse(timestamp_str)

    previous = previous_by_run_id(
        run_id=run_id, account_id=account_id, product_id=product_id
    )
    if previous:
        last_run = Change(
            old_value=previous.amount,
            new_value=amount,
            from_date=parse(previous.timestamp),
            to_date=timestamp,
        )
        last_run_change_str = last_run.change_str

    previous = previous_by_days_elapsed(
        account_id=account_id, product_id=product_id, days=7
    )
    if previous:
        weekly_change = Change(
            old_value=previous.amount,
            new_value=amount,
            from_date=parse(previous.timestamp),
            to_date=timestamp,
        )
        weekly_change_str = weekly_change.change_str

    previous = previous_by_days_elapsed(
        account_id=account_id, product_id=product_id, days=30
    )
    # if not previous:
    #     previous = first_entry(account_id=account_id, product_id=product_id)
    if previous:
        monthly_change = Change(
            old_value=previous.amount,
            new_value=amount,
            from_date=parse(previous.timestamp),
            to_date=timestamp,
        )
        monthly_change_str = monthly_change.change_str

    previous = first_entry(account_id=account_id, product_id=product_id)
    if previous:
        # alltime_change, _ = change_str(
        #     amount=amount,
        #     timestamp=timestamp,
        #     previous_amount=previous.amount,
        #     previous_timestamp=previous.timestamp,
        # )
        alltime_change = Change(
            old_value=previous.amount,
            new_value=amount,
            from_date=parse(previous.timestamp),
            to_date=timestamp,
        )
        alltime_change_str = alltime_change.change_str
        if not alltime_change_str:
            warn(f"first entry exists, but all time change is blank")
            ic(previous)
            ic(timestamp)
        days = (timestamp - parse(previous.timestamp)).days
        if days > 30 and alltime_change.change > 0:
            apr_new = alltime_change.apr
            apr_old = calc_apr(principal=previous.amount, change = amount - previous.amount, days=days)
            alltime_change_str += f" {alltime_change.timespan} {round(apr_old,1)}% apr"

    return Changes(
        last_run=last_run_change_str,
        weekly=weekly_change_str,
        monthly=monthly_change_str,
        alltime=alltime_change_str,
    )

if __name__ == "__main__":
    # from datetime import datetime
    init(421)
    run_id, timestamp = get_last_run_id()
    account_id = 1
    product_id = 1
    amount = 100
    changes = get_change_overtime(run_id=run_id, account_id=account_id, product_id=product_id, amount=amount, timestamp_str=timestamp)
    ic(changes.alltime)
