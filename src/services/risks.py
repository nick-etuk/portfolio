from lib import named_tuple_factory
import sqlite3 as sl
from config import db
from init import log
from dateutil.parser import parse
from icecream import ic
from tabulate import tabulate
from init import init, log
from totals import get_totals
import pandas as pd

from lib import named_tuple_factory
import sqlite3 as sl
from config import db
from init import log
from dateutil.parser import parse
from icecream import ic
from tabulate import tabulate
from init import init, log
from totals import get_totals
import pandas as pd
from risk_product_too_high_risk import product_too_high_risk
from risk_high_risk_products import high_risk_products
from risk_medium_risk_products import medium_risk_products
from risk_auto_funds_managers import auto_fund_managers


def to_html(violations):
    output = f"<h2 style='color:red'>Risk Violations</h2>"
    for violation in violations:
        output += f"<h2>{violation['descr']}</h2>"
        for instance in violation['instances']:
            output += f"<p>{instance}</p>"

    return output


def check_risks():
    combined_total, solomon_total, personal_total, details, table = get_totals(
        "total")
    print('Combined total is', round(combined_total))

    rules = [
        {
            'rule_id': 1,
            'descr': rf"No more than 10% (6500 - should be {round(combined_total * 0.1)}) in a single product, regardless of risk.",
            'function': medium_risk_products

        },
        {
            'rule_id': 2,
            'descr': rf"No more than 20% (should be {round(combined_total * 0.4)} - manually set to 13K) with one fund manager.",
            'function': auto_fund_managers

        },
        {
            'rule_id': 3,
            'descr': rf"No more than 5% (should be {round(combined_total * 0.05)} - manually set to 850) in a high risk product.",
            'function': high_risk_products

        },
        {
            'rule_id': 4,
            'descr': rf"Product too high risk for account",
            'function': product_too_high_risk
        }
    ]

    result = []
    for rule in rules:
        instances = rule['function'](combined_total)
        if instances:
            result.append({**rule, 'instances': instances})

    ic(result)

    return to_html(result) if result else ''


if __name__ == "__main__":
    #solomon_total, personal_total, details = get_totals("total")
    # log(tabulate(details, headers="firstrow"))
    init()
    print(check_risks())
    # print(high_risk_products(0000))
    # print(medium_risk_products(0000))
