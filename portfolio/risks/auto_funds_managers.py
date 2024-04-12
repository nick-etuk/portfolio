from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from icecream import ic


def get_details(manager: str):
    sql = """
    select ac.account_id, ac.descr as account, p.descr as product, p.chain, act.amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join account ac
    on ac.account_id=act.account_id
    inner join instrument_status inst
    on inst.account_id=act.account_id
    and inst.product_id=act.product_id
    where act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and inst.effdt=(
        select max(effdt) from instrument_status
        where account_id=inst.account_id
        and product_id=inst.product_id
    )
    and inst.instrument_status='OPEN'
    and p.manager = ?
    and act.status='A'
    """
    details = ""
    total = 0

    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (manager,)).fetchall()

    for row in rows:
        details += f"""
        <tr>
            <td>{row.account}</td>
            <td>{row.product}</td>
            <td>{row.chain}</td>
            <td>{row.amount}</td>
        </tr>
        """
        total += row.amount

    return details, total


def auto_fund_managers(combined_total: float):
    """
    No more than 2 medium security lots in beefy, grizzly or any other automated fund manager.
    i.e max of 6500 * 2 managed by beefy.
    no more than 40% of total value in one automated fund manager.
    """

    sql = """
    select p.manager, sum(act.amount) as amount
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    inner join instrument_status inst
    on inst.account_id=act.account_id
    and inst.product_id=act.product_id
    where act.status='A'
    and p.manager <> ' '
    and act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and inst.effdt=(
        select max(effdt) from instrument_status
        where account_id=inst.account_id
        and product_id=inst.product_id
    )
    and inst.instrument_status='OPEN'
    group by p.manager
    having sum(act.amount) > ?
    """
    # max_amount = combined_total * 0.4
    max_amount = 6500 * 2
    instances = []
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (max_amount,)).fetchall()

    if not rows:
        return instances

    for row in rows:
        detail_header = f"""
        <p>{row.manager}. Reduce by {round(row.amount - max_amount)}</p>
        <table>
            <tr>
                <td>Account</td>
                <td>Product</td>
                <td>Chain</td>
                <td>Amount</td>
            </tr>
        """
        detail_rows, detail_total = get_details(row.manager)

        detail_footer = f"""
        <tr>
            <td></td>
            <td></td>
            <td>Total</td>
            <td>{detail_total}</td>
        </tr>
        </table>
        """

        instances.append(detail_header + detail_rows + detail_footer)

    return instances
