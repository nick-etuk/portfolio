import numpy as np
from init import init, log
from lib import named_tuple_factory, previous_values_by_run_id, previous_values_days_ago, first_entry, get_debts_by_product
import sqlite3 as sl
from config import db
from dateutil.parser import parse
from icecream import ic
from changes import get_last_run_id, change_str

# table = []


def get_products(run_id, timestamp, account_id, account, mode):
    total = 0

    cash_filter = "and p.cash='Y'" if mode == "cash" else ""

    sql = f"""
    select act.product_id, p.descr as product, risk.risk_level_descr, p.chain, sum(act.amount) as amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join risk_category risk
    on risk.id = p.risk_category
    where act.account_id=?
    and act.status='A'
    and p.subtotal='N'
    {cash_filter}
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    group by act.product_id, p.descr
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (account_id,)).fetchall()

    debts = get_debts_by_product(account_id)
    result_dict = []
    result_table = []

    for product in rows:
        amount = product.amount
        if product.product_id in debts:
            amount -= debts[product.product_id]

        change = ""
        previous = previous_values_by_run_id(
            run_id=run_id, account_id=account_id, product_id=product.product_id)
        if previous:
            change = change_str(amount=amount, timestamp=timestamp,
                                previous_amount=previous.amount, previous_timestamp=previous.timestamp)

        weekly_change = ""
        previous = previous_values_days_ago(
            account_id=account_id, product_id=product.product_id, days=7)
        if previous:
            weekly_change = change_str(amount=amount, timestamp=timestamp,
                                       previous_amount=previous.amount, previous_timestamp=previous.timestamp)

        monthly_change = ""
        previous = previous_values_days_ago(
            account_id=account_id, product_id=product.product_id, days=30)
        if not previous:
            previous = first_entry(
                account_id=account_id, product_id=product.product_id)
        if previous:
            monthly_change = change_str(amount=amount, timestamp=timestamp,
                                        previous_amount=previous.amount, previous_timestamp=previous.timestamp)

        result_dict.append(
            {product.product: {
                'amount': round(amount, 0),
                'risk': product.risk_level_descr,
                'chain': product.chain,
                'change': change,
                'week': weekly_change,
                'month': monthly_change
            }
            })
        result_table.append([account, product.product, round(
            amount, 0), product.risk_level_descr, product.chain, change, weekly_change, monthly_change])
        total += amount

    return total, result_dict, result_table


def get_assets(account):
    total = 0
    sql = """
    select lo.borrower_id, bo.descr as borrower, sum(lo.amount) as amount
    from loan lo
    inner join account bo
    on bo.account_id=lo.borrower_id
    where lo.lender_id=?
    and lo.status='A'
    group by lo.borrower_id, bo.descr
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (account.account_id,)).fetchall()

    results = []
    result_table = []

    for loan in rows:
        results.append({'Loan to '+loan.borrower: round(loan.amount, 0)})
        total += loan.amount
        result_table.append([account.account, 'Loan to '+loan.borrower, round(
            loan.amount, 0), '', '', ''])

    return total, results, result_table


def get_debts(account):
    total = 0
    sql = """
    select lo.lender_id, lend.descr as lender, sum(lo.amount) as amount
    from loan lo
    inner join account lend
    on lend.account_id=lo.lender_id
    where lo.borrower_id=?
    and lo.status='A'
    group by lo.lender_id, lend.descr
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (account.account_id,)).fetchall()

    results = []
    for loan in rows:
        results.append({'Owed to '+loan.lender: round(loan.amount, 0)})
        total += loan.amount

    return total, results


def get_totals(mode: str, account_id: int = 0):
    run_id, timestamp = get_last_run_id()

    account_filter = ""
    args = ()
    if account_id:
        account_filter = "and ac.account_id=?"
        args = (account_id,)

    solomon_total = 0
    personal_total = 0

    sql = f"""
    select ac.account_id, ac.descr as account
    from account ac
    where 1=1
    {account_filter}
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, args).fetchall()

    result_dict = {}

    result_table = []
    for account in rows:
        result_list = []
        total = 0

        prod_total, products, prod_rows = get_products(
            run_id=run_id, timestamp=timestamp, account_id=account.account_id, account=account.account, mode=mode)
        if products:
            # result_list.append(products)
            for item in products:
                result_list.append(item)
            total = prod_total
            for row in prod_rows:
                result_table.append(row)

        if not mode == "cash":
            asset_total, assets, asset_rows = get_assets(account)
            if assets:
                result_list.append(assets)
                total += asset_total
                for row in asset_rows:
                    result_table.append(row)

            debt_total, debts = 0, {}  # get_debts(account)
            if debts:
                result_list.append(debts)
                total -= debt_total

        if not total == 0:
            result_list.append({'Total': round(total, 0)})

        if result_list:
            result_dict[account.account] = result_list

        if account.account.startswith('Solomon'):
            solomon_total += total
        else:
            personal_total += total

    return round(solomon_total+personal_total, 0), round(solomon_total, 0), round(personal_total, 0), result_dict, result_table


def show_totals(mode):
    total, solomon_total, personal_total, result_dict, result_table = get_totals(
        mode)
    log(f"Solomon {mode}: {solomon_total}")
    log(f"Personal {mode}: {personal_total}")
    log(f"Combined {mode}: {total}")
    #print('totals table 0:', result_table, "\n")
    return result_table
    # return np.sort(table, axis=0)


if __name__ == "__main__":
    init()
    result = show_totals("total")
    # show_totals("cash")
    print(result)
