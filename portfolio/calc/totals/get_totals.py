import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory
from portfolio.utils.init import info
from portfolio.calc.totals.get_total_products import get_total_products
from portfolio.calc.totals.total_class import TotalClass
from icecream import ic


def get_totals(run_id, timestamp, totals_mode, account_id=0) -> TotalClass:
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

    totals_table = []
    for account_row in rows:
        # account_total = 0

        account_total, product_dict_rows = get_total_products(
            run_id=run_id,
            timestamp=timestamp,
            account_id=account_row.account_id,
            account=account_row.account,
            totals_mode=totals_mode,
        )
        # ic(account, account_total, products, prod_rows)
        info(f"Totals: {account_row.account} {account_total}")
        if product_dict_rows:
            # result_list.append(products)
            for item in product_dict_rows:
                totals_table.append(item)
            #      item schema is { "product": row.product,
            #     "amount": round(amount),
            #     "risk": row.risk_level_descr,
            #     "chain": row.chain,
            #     "last_updated": last_updated_str,
            #     "change": change.last_run,
            #     "week": change.weekly,
            #     "month": change.monthly,
            #     "alltime": change.alltime,
            #     "apr": change.apr,
            # }
                # result_table.append(
                #     [
                #         account_row.account,
                #         row.product,
                #         round(amount),
                #         row.risk_level_descr,
                #         row.chain,
                #         last_updated_str,
                #         change.last_run,
                #         change.weekly,
                #         change.monthly,
                #         change.alltime,
                #     ]
                # )


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

        # if account_total != 0:
        #     result_list.append({"Total": round(account_total)})

        # if result_list:
        #     result_dict[account_row.account] = result_list

        totals_table.sort(key=lambda x: x["alltime_apr"])

        if account_row.account.startswith("Solomon"):
            solomon_total += account_total
        else:
            personal_total += account_total

    return TotalClass(
        solomon=solomon_total,
        personal=personal_total,
        totals_table=totals_table
    )

    # return (
    #     round(solomon_total + personal_total, 0),
    #     round(solomon_total, 0),
    #     round(personal_total, 0),
    #     result_dict,
    #     result_table,
    # )
