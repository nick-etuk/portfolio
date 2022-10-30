from lib import named_tuple_factory
import sqlite3 as sl
from config import db
from dateutil.parser import parse
from icecream import ic
from init import log

old_sql = """
select seq, timestamp, amount
from actual_total act
where account_id=?
and product_id=?
and seq=
    (select max(seq) from actual_total
    where account_id=act.account_id
    and product_id=act.product_id
    and seq<?)
    """


def calc_apr(principal: float, change: float, days: float):
    years = days/365
    apr = (change/(years*principal))*100
    return apr


if __name__ == "__main__":
    log(calc_apr(48087, 2404.35, 365))
    log(calc_apr(48087, 6.587260274, 1))
    log(calc_apr(48087, 6.587260274, 1))
    log(calc_apr(48087, 2404.35/2, 365/2))
