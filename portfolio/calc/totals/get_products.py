from datetime import datetime
from dateutil.parser import parse
import sqlite3 as sl
from portfolio.calc.change_over_time import get_change_overtime
from portfolio.calc.changes import days_ago
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory


def get_products(run_id, timestamp, account_id, account, totals_mode):
    account_total = 0

    cash_filter = "and p.cash='Y'" if totals_mode == "cash" else ""

    # select act.product_id, p.descr as product, risk.risk_level_descr, p.chain, sum(act.amount) as amount
    sql = f"""
    select act.product_id, p.descr as product, risk.risk_level_descr, p.chain, 
    act.amount, act.timestamp
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    left outer join risk_category risk
    on risk.id=p.risk_category
    where act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        -- and run_id=act.run_id
        )
    and act.account_id=?
    -- and act.run_id = ?
    and act.status='A'
    and p.subtotal='N'
    and act.dummy = 'N'
    {cash_filter}
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (account_id,)).fetchall()

    # debts = get_debts_by_product(account_id)
    result_dict = []
    result_table = []

    for product in rows:
        amount = product.amount
        # if product.product_id in debts:
        #     amount -= debts[product.product_id]

        changes = get_change_overtime(
            run_id=run_id,
            account_id=account_id,
            product_id=product.product_id,
            amount=amount,
            timestamp=timestamp,
        )

        result_dict.append(
            {
                product.product: {
                    "amount": round(amount),
                    "risk": product.risk_level_descr,
                    "chain": product.chain,
                    "last_updated": product.timestamp,
                    "change": changes.last_run,
                    "week": changes.weekly,
                    "month": changes.monthly,
                    "alltime": changes.alltime,
                }
            }
        )
        result_table.append(
            [
                account,
                product.product,
                round(amount),
                product.risk_level_descr,
                product.chain,
                days_ago(datetime.now(), parse(product.timestamp)),
                changes.last_run,
                changes.weekly,
                changes.monthly,
                changes.alltime,
            ]
        )
        account_total += amount

    return round(account_total), result_dict, result_table
