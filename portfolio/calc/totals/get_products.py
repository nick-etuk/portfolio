from datetime import datetime
from dateutil.parser import parse
import sqlite3 as sl
from portfolio.calc.changes.change_over_time import get_change_overtime
from portfolio.calc.changes.days_ago import days_ago
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
    and p.product_id <> '3'
    and p.data_source <> 'MORALIS_TOKEN_API'
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

    for row in rows:
        amount = row.amount
        # if product.product_id in debts:
        #     amount -= debts[product.product_id]

        changes = get_change_overtime(
            run_id=run_id,
            account_id=account_id,
            product_id=row.product_id,
            amount=amount,
            timestamp_str=timestamp,
        )

        prev_timestamp = parse(row.timestamp)
        if (datetime.now() - prev_timestamp).days > 2:
            last_updated_str = days_ago(datetime.now(), prev_timestamp)
        else:
            last_updated_str = ""

        result_dict.append(
            {
                row.product: {
                    "amount": round(amount),
                    "risk": row.risk_level_descr,
                    "chain": row.chain,
                    "last_updated": last_updated_str,
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
                row.product,
                round(amount),
                row.risk_level_descr,
                row.chain,
                last_updated_str,
                changes.last_run,
                changes.weekly,
                changes.monthly,
                changes.alltime,
            ]
        )
        account_total += amount

    return round(account_total), result_dict, result_table
