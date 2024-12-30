import inspect
import sqlite3 as sl
from portfolio.calc.debts_by_product import net_amount
from portfolio.utils.config import db
from portfolio.utils.dict_to_object import AttrDict
from portfolio.utils.init import info, warn
from portfolio.utils.lib import named_tuple_factory


def previous_by_run_id(run_id, account_id, product_id):
    # print(f"{inspect.stack()[0][3]}: {run_id=}, {account_id=}, {product_id=}")
    prev_run_id_sql = """
    select max(run_id) as max_run_id from actual_total
    where account_id=?
    and product_id=?
    and run_id<?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        prev_row = c.execute(prev_run_id_sql, (account_id, product_id, run_id)).fetchone()

    if not prev_row:
        warn(f"No previous run_id found for {run_id}, {account_id}, {product_id}")
        return None
    
    prev_run_id = prev_row.max_run_id

    sql = """
    select run_id, timestamp, amount
    from actual_total act
    where act.seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id)
    and act.run_id=?
    and account_id=?
    and product_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (prev_run_id, account_id, product_id,)).fetchone()
    if not row:
        warn(f"No previous record found for {run_id}, {account_id}, {product_id}")
        return None

    # info(f"previous_by_run_id: account: {account_id} product: {product_id}")
    # info(f"run_id: {run_id} prev_run_id: {prev_run_id} prev amount: {row.amount}")

    return AttrDict(
        {
            "run_id": row.run_id, 
            "timestamp": row.timestamp, 
            "amount": row.amount
        }
    )
    # return {
    #     "run_id": row.run_id, 
    #     "timestamp": row.timestamp, 
    #     "amount": row.amount
    # }
