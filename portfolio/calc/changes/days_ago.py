from datetime import datetime
from icecream import ic

def plural(number: float, label: str) -> str:
    # number_str = "{:.0f}".format(number).strip("0").strip(".")
    number_str = str(round(number))
    if number_str == "1":
        return f"{number_str} {label}"
    return f"{number_str} {label}s"

def days_ago(new_timestamp: datetime, old_timestamp: datetime):
    delta = new_timestamp - old_timestamp
    seconds = delta.total_seconds()
    days = seconds / 60 / 60 / 24

    if days > 365:
        years = days / 365
        label = "year" if round(years) == 1 else "years"
        # number_str = "{:.1f}".format(years).strip("0").strip(".")
        number_str = str(round(years,1))
        return f"{number_str} {label}"

    if days > 30:
        months = days / 30
        return plural(months, "month")

    if days > 7:
        weeks = days / 7
        return plural(weeks, "week")

    if days >= 1:
        return plural(days, "day")

    hours = seconds / 60 / 60
    if hours >= 1:
        return plural(hours, "hour")
    
    minutes = seconds / 60
    if minutes >= 1:
        return plural(minutes, "minute")

    return ""
