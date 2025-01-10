import inspect
from dateutil.parser import parse
from portfolio.calc.changes.change_classes import Change
# from portfolio.calc.debts_by_product import net_amount
from portfolio.calc.previous.previous_by_run_id import previous_by_run_id
from portfolio.utils.lib import (
    named_tuple_factory,
    get_last_run_id,
)
import sqlite3 as sl
from portfolio.utils.config import db
from icecream import ic
from portfolio.utils.init import info, init, log
from portfolio.calc.changes.change_str import change_str


account_col = ""
product_col = ""
amount_col = 0
change_col = ""
table = []


def get_product_changes(run_id, account_id, account):
    # print(f"{__name__}.{inspect.stack()[0][3]}")
    # print(f"run_id: {run_id} account: {account}")

    sql = """
    select act.product_id, p.descr as product, p.volatile, act.amount, act.timestamp
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    where act.run_id = ?
    and act.account_id=?
    -- and p.subtotal='N' why exclude subtotals?
    and act.status='A'
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (run_id, account_id,),).fetchall()

    results = []
    for row in rows:
        # amount = net_amount(
        #     product.amount, account_id=account_id, product_id=product.product_id
        # )
        amount = row.amount
        # print(f"{row.product_id=}, {row.product=}, {amount=}")
        change = ""
        previous = previous_by_run_id(
            run_id=run_id, account_id=account_id, product_id=row.product_id
        )

        if previous:
            # change, apr = change_str(
            #     amount=amount,
            #     timestamp=row.timestamp,
            #     previous_amount=previous.amount,
            #     previous_timestamp=previous.timestamp,
            # )
            change = Change(old_value= previous.amount,
                            new_value=amount,
                            from_date=parse(previous.timestamp),
                            to_date=parse(row.timestamp))

        if change.change != 0:
            info(f"Changes: {account} {row.product} {round(amount)} {change.change} {change.timespan}")
            # table.append([account, product.product, amount, change])

            # results.append(                {product.product: {"amount": amount, "change": change, "apr": apr}}            )
            results.append(
                {
                    "account": account,
                    "product": row.product,
                    "amount": amount,
                    "change": change.change,
                    "apr": change.apr,
                    "timespan": change.timespan,
                }
            )
    return results


def get_account_changes(run_id):
    print(f"{__name__}.{inspect.stack()[0][3]}")

    account_sql = """
    select distinct act.run_id, act.account_id, ac.descr as account
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    where act.run_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        account_rows = c.execute(account_sql, (run_id,)).fetchall()

    results_array = []
    for account_row in account_rows:
        prod_results = get_product_changes(account_row.run_id, account_row.account_id, account_row.account)
        if prod_results:
            for prod_row in prod_results:
                results_array.append(prod_row)
    results_array.sort(key=lambda x: x["apr"], reverse=True)
    return results_array


def report_changes(run_id):
    print(f"{__name__}.{inspect.stack()[0][3]}")
    result = get_account_changes(run_id)
    return result


if __name__ == "__main__":
    init()
    run_id, _ = get_last_run_id()
    result = report_changes(run_id)
    ic(result)
    # print(report_changes(run_id))
