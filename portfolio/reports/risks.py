from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from dateutil.parser import parse
from icecream import ic


def get_products(account):
    total = 0
    sql = """
    select act.product_id, p.descr as product, sum(act.amount) as amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    where act.account_id=?
    and p.subtotal='N'
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    group by act.product_id, p.descr
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (account.account_id,)).fetchall()

    results = []
    for product in rows:
        results.append({product.product: {'amount': product.amount}})
        total += product.amount

    return total, results


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
    for loan in rows:
        results.append({'Loan to '+loan.borrower: loan.amount})
        total += loan.amount

    return total, results


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
        results.append({'Owed to '+loan.lender: loan.amount})
        total += loan.amount

    return total, results


def accounts():
    solomon_total = 0
    personal_total = 0
    sql = """
    select ac.account_id, ac.descr as account
    from account ac
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql,).fetchall()

    result_dict = {}
    for account in rows:
        result_list = []

        prod_total, products = get_products(account)
        asset_total, assets = get_assets(account)
        debt_total, debts = get_debts(account)

        if products:
            result_list.append(products)
        if assets:
            result_list.append(assets)
        if debts:
            result_list.append(debts)

        total = prod_total + asset_total - debt_total
        result_list.append({'Total': total})
        result_dict[account.account] = result_list

        if account.account.startswith('Solomon'):
            solomon_total += total
        else:
            personal_total += total

    return solomon_total, personal_total, result_dict


if __name__ == "__main__":
    solomon_total, personal_total, details = accounts()
    ic(details)
    print(f"Solomon total: {solomon_total}")
    print(f"Personal total: {personal_total}")
