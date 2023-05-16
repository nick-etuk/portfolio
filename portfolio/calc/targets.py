from datetime import datetime
from webbrowser import get

import numpy as np
from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.init import log
from dateutil.parser import parse
from icecream import ic
from tabulate import tabulate
from portfolio.utils.init import init, log
from portfolio.calc.totals import get_totals
import pandas as pd

table = []


def accrued_amount(principal: float, rate: float, days: float):
    result = principal * (1 + rate * (days / 365) / 100)
    # print(f"principal: {principal}, rate: {rate}, days: {days}. Accrued = {result} ")
    return result


def get_targets(account_id):
    total_principal = 0
    total_accrued = 0

    sql = """
    select f.account_id, f.date, f.amount_usd
    from funding f
    where f.account_id=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (account_id,)).fetchall()

    for funding_row in rows:
        current_timestamp = datetime.now()
        prev_timestamp = parse(funding_row.date)
        delta = current_timestamp - prev_timestamp
        seconds = delta.total_seconds()
        days = seconds / 60 / 60 / 24

        sql = """
        select target_rate 
        from account
        where account_id = ?
        """
        with sl.connect(db) as conn:
            conn.row_factory = named_tuple_factory
            c = conn.cursor()
            rate_row = c.execute(sql, (funding_row.account_id,)).fetchone()

        target_rate = rate_row.target_rate
        target_amount = accrued_amount(
            principal=funding_row.amount_usd, rate=target_rate, days=days
        )

        total_principal += funding_row.amount_usd
        total_accrued += target_amount

    return total_principal, total_accrued


def get_target_accounts():
    sql = """
    select distinct f.account_id , ac.descr as account
    from funding f
    inner join account ac
    on ac.account_id=f.account_id
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    for row in rows:
        principal, accrued = get_targets(row.account_id)
        (
            current_value,
            solomon_total,
            personal_total,
            details,
            totals_table,
        ) = get_totals("total", row.account_id)
        table.append(
            [
                row.account,
                principal,
                round(accrued),
                round(current_value),
                round(accrued - current_value),
            ]
        )
        # print(f"{row.account} -  \t\t\t Invested:{principal}, \t\t expected: {round(accrued)} current: {round(current_value)}, shortfall: {round(accrued-current_value)}")

    return table


def targets():
    result = get_target_accounts()
    # r2 = np.sort(result, axis=0)
    return result


if __name__ == "__main__":
    # solomon_total, personal_total, details = get_totals("total")
    # log(tabulate(details, headers="firstrow"))
    init()
    result = targets()
    ic(result)
