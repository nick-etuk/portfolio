from portfolio.calc.changes import change_str
from portfolio.calc.debts_by_product import net_amount
from portfolio.utils.dict_to_object import AttrDict
from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from dateutil.parser import parse


def get_prevous_by_timestamp(
    current_seq,
    account_id,
    account,
    product_id,
    product,
    current_amount,
    current_timestamp,
):
    sql = """
    select run_id, seq, timestamp, amount
    from actual_total act
    where account_id=?
    and product_id=?
    and timestamp=
        (select max(timestamp) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and timestamp < ?)
    and seq < ?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(
            sql, (account_id, product_id, current_timestamp, current_seq)
        ).fetchone()

    if not row:
        return

    change, _ = change_str(
        amount=current_amount,
        timestamp=current_timestamp,
        previous_amount=row.amount,
        previous_timestamp=row.timestamp,
    )

    if change:
        timestamp = parse(current_timestamp)
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H")

        print(f"{formatted_timestamp} {account} {product} {current_amount} {change}")

    """
    get_prevous_by_timestamp(
        current_seq=previous.seq,
        account_id=account_id,
        account=account,
        product_id=product_id,
        product=product,
        current_amount=previous.amount,
        current_timestamp=previous.timestamp,
    )
    """
    # amount = net_amount(row.amount, account_id, product_id)
    return AttrDict(
        {
            "seq": row.seq,
            "run_id": row.run_id,
            "timestamp": row.timestamp,
            "amount": row.amount,
            "change": change,
        }
    )
