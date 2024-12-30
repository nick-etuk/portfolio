from dateutil.parser import parse
from portfolio.calc.changes.days_ago import days_ago
from portfolio.calc.changes.apr import calc_apr


def change_str(amount, timestamp, previous_amount, previous_timestamp):
    if not (previous_amount and previous_timestamp):
        return "New entry", 0

    change = amount - previous_amount
    current_timestamp = parse(timestamp)
    prev_timestamp = parse(previous_timestamp)
    delta = current_timestamp - prev_timestamp
    seconds = delta.total_seconds()
    days = seconds / 60 / 60 / 24

    apr = calc_apr(previous_amount, change, days)

    change_str = ""
    if change >= 0.5:
        change_str = "{:+.0f}".format(change)
        # days_str1 = "day" if round(days) == 1 else "days"
        # days_str2 = "{:.1f}".format(days).strip("0").strip(".")
        # days_str = days_str2 + " " + days_str1
        timespan = days_ago(current_timestamp, prev_timestamp)
        # days_str = f"{days:g} {days_str1}"
        if apr > 0.1:
            # change_str += "  " + "{:.0f}".format(apr) + "%  " + days_str
            change_str = "{:.0f}".format(apr) + "%  " + timespan
        else:
            change_str += "  " + timespan

    return change_str, apr
