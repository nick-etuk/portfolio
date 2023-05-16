from icecream import ic
from portfolio.calc.changes import get_accounts
from portfolio.calc.targets import get_target_accounts
from portfolio.utils.lib import get_last_run_id


def interest_rate_too_high(combined_total: float):
    """
    APR should not be higher than 20%.
    """
    last_run_id, timestamp = get_last_run_id()
    changes = get_accounts(last_run_id)
    instances = []
    for account in changes.items():
        for products in account[1]:
            for product in products.items():
                apr = product[1]["apr"]
                change_str = product[1]["change"]
                if apr > 20:
                    instances.append(f"{account[0]} {product[0]} {change_str}")

    return instances


if __name__ == "__main__":
    ic(interest_rate_too_high(0))
