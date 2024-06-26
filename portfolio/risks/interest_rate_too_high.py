import inspect
from icecream import ic
from portfolio.calc.changes import get_accounts
from portfolio.utils.lib import get_last_run_id


def interest_rate_too_high(combined_total: float):
    """
    APR should not be higher than 20%.
    """
    print(f"{__name__}.{inspect.stack()[0][3]}")

    last_run_id, timestamp = get_last_run_id()
    changes = get_accounts(last_run_id)
    instances = []
    for product in changes:
        apr = product["apr"]
        change_str = product["change"]
        if apr > 20:
            instances.append(f"{product['account']} {product['product']} {change_str}")

    return instances


if __name__ == "__main__":
    ic(interest_rate_too_high(0))
