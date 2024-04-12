from icecream import ic
from portfolio.utils.init import init, log
from portfolio.risks.ip_address_changed import ip_address_changed
from portfolio.calc.totals import get_totals

from portfolio.risks.product_too_high_risk import product_too_high_risk
from portfolio.risks.high_risk_products import high_risk_products
from portfolio.risks.medium_risk_products import medium_risk_products
from portfolio.risks.auto_funds_managers import auto_fund_managers
from portfolio.risks.interest_rate_too_high import interest_rate_too_high


def to_html(violations):
    output = f"<h2 style='color:red'>Risks</h2>"
    for violation in violations:
        output += f"<h2>{violation['descr']}</h2>"
        for instance in violation["instances"]:
            output += f"<div>{instance}</div>"

    return output


def check_risks():
    combined_total, solomon_total, personal_total, details, table = get_totals("total")
    print("Combined total is", round(combined_total))

    rule_factory = [
        {
            "rule_id": 1,
            # 'descr': rf"No more than 10% ({round(combined_total * 0.1)}) in a single product, regardless of risk.",
            "descr": "No more than 6500 in a single product, regardless of risk.",
            "function": medium_risk_products,
        },
        {
            "rule_id": 2,
            # 'descr': rf"No more than 20% ({round(combined_total * 0.4)}) with one automated fund manager.",
            "descr": "No more than 13K with one automated fund manager.",
            "function": auto_fund_managers,
        },
        {
            "rule_id": 3,
            # 'descr': f"No more than 5% (should be {round(combined_total * 0.05)} - manually set to 850) in a high risk product.",
            "descr": "No more than 850 in one high risk product.",
            "function": high_risk_products,
        },
        {
            "rule_id": 4,
            "descr": "Product too high risk for account",
            "function": product_too_high_risk,
        },
        {
            "rule_id": 5,
            "descr": f"Very high interest rate. Could be risky.",
            "function": interest_rate_too_high,
        },
        {
            "rule_id": 6,
            "descr": "Your IP address has changed. Update Binance API whitelist and AWS security groups.",
            "function": ip_address_changed,
        },
    ]

    result = []
    for rule in rule_factory:
        instances = rule["function"](combined_total)
        if instances:
            result.append({**rule, "instances": instances})

    # ic(result)

    return to_html(result) if result else ""


if __name__ == "__main__":
    # solomon_total, personal_total, details = get_totals("total")
    # log(tabulate(details, headers="firstrow"))
    init()
    print(check_risks())
    # print(high_risk_products(0000))
    # print(medium_risk_products(0000))
