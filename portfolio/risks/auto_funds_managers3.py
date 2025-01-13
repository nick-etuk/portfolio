import inspect
from portfolio.risks.auto_funds_managers import get_product_details_by_manager
from portfolio.utils.lib import named_tuple_factory
import sqlite3 as sl
from portfolio.utils.config import db
from icecream import ic


def auto_fund_managers3(combined_total: float):
    print(f"{__name__}.{inspect.stack()[0][3]}")
    """
    No more than 2 positions with any other automated fund manager.
    """
    sql = """
    select act.product_id, p.manager, count(*) as product_count
    from actual_total act
    inner join product p
    on p.product_id=act.product_id
    where act.seq=
        (select max(seq) from actual_total
        where product_id=act.product_id)
    and act.status='A'
    and p.manager <> ' '
    group by p.manager
    having count(*) > 2
    """
    instances = []
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql).fetchall()

    if not rows:
        return None

    for row in rows:
        detail_header = f"""
        <p>Too many products managed by {row.manager}</p>
        <table>
            <tr>
                <td>Account</td>
                <td>Product</td>
                <td>Chain</td>
                <td>Amount</td>
            </tr>
        """
        detail_rows, detail_total = get_product_details_by_manager(row.manager)

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
