import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.init import info
from portfolio.utils.lib import named_tuple_factory
from portfolio.calc.totals.get_products import get_products
from portfolio.calc.totals.total_class import TotalClass
from icecream import ic


def get_totals(run_id, timestamp, totals_mode, account_id=0):
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
        # account_total = 0

        account_total, products, prod_rows = get_products(
            run_id=run_id,
            timestamp=timestamp,
            account_id=account.account_id,
            account=account.account,
            totals_mode=totals_mode,
        )
        # ic(account, account_total, products, prod_rows)
        info(f"{account.account} total: {account_total}")
        if products:
            # result_list.append(products)
            for item in products:
                result_list.append(item)
            for row in prod_rows:
                result_table.append(row)

        """
        if mode != "cash":
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
        """

        if account_total != 0:
            result_list.append({"Total": round(account_total)})

        if result_list:
            result_dict[account.account] = result_list

        if account.account.startswith("Solomon"):
            solomon_total += account_total
        else:
            personal_total += account_total

    return TotalClass(
        solomon=solomon_total,
        personal=personal_total,
        totals_dict=result_dict,
        totals_table=result_table,
    )

    # return (
    #     round(solomon_total + personal_total, 0),
    #     round(solomon_total, 0),
    #     round(personal_total, 0),
    #     result_dict,
    #     result_table,
    # )
