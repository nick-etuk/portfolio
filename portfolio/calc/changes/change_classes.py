from dateutil.parser import parse
from portfolio.calc.changes.apr import calc_apr
from portfolio.calc.changes.days_ago import days_ago


class Change:
    def __init__(self, old_value: float, new_value: float, from_date: any, to_date: any):
        if isinstance(from_date, str):
            from_date = parse(from_date)
        if isinstance(to_date, str):
            from_date = parse(to_date)
        self.change = new_value - old_value
        change_str = "" if self.change >= -0.5 and self.change <= 0.5 else "{:+.0f}".format(self.change)
        self.change_str = change_str
        self.percent = self.change / old_value if old_value else 0
        self.days = (to_date - from_date).days
        self.daily_change = self.change / self.days if self.days else 0

        self.apr = 0
        if old_value and self.change > 0:
            self.apr = calc_apr(principal=old_value, change=self.change, days=self.days)
            # apr_new = self.daily_change * 365 / old_value if old_value else 0

        self.timespan = days_ago(new_timestamp=to_date, old_timestamp=from_date)

class ChangeOverTime:
    def __init__(self, last_run: str, weekly: str, monthly: str, alltime: str, alltime_apr: float):
        self.last_run = last_run
        self.weekly = weekly
        self.monthly = monthly
        self.alltime = alltime
        self.alltime_apr = alltime_apr