import sqlite3 as sl
import sys
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory


def add_new(run_id: int):
    sql = """
    insert into instrument_status (account_id, product_id, instrument_status, effdt, absence_count, run_id)
    select distinct account_id, product_id, 'OPEN' as instrument_status, 
    current_timestamp as effdt, 0 as absence_count, run_id
    from actual_total act
    where not exists
        (select 1 from instrument_status inst
        where inst.account_id=act.account_id 
        and inst.product_id=act.product_id)
    and act.run_id=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(sql, (run_id,))


def reopen_closed_instruments(run_id: int):
    """
    ready to code
    select distinct account/product combinations in the current fetch
    where the current instrument status is closed

    insert a row into instrument_status with
    absence count=1 and instrument_status is PENDING_CLOSE
    """
    sql = """
    insert into instrument_status (account_id, product_id, instrument_status, effdt, absence_count, run_id)
    select account_id, product_id, 'OPEN' as instrument_status, 
    current_timestamp as effdt, 0 as absence_count, run_id
    from actual_total act
    where not exists (
            select 1 from instrument_status inst
            where inst.account_id=act.account_id 
            and inst.product_id=act.product_id
            and inst.instrument_status in ('PENDING_CLOSE', 'CLOSED')
            and inst.effdt=(
                select max(effdt) from instrument_status
                where account_id=inst.account_id
                and product_id=inst.product_id
                )
        )
    and act.run_id=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(sql, (run_id,))


def prepare_to_close(run_id: int):
    """
    abandon
    select  act.account_id, act.product_id, 'PENDING_CLOSE' as instrument_status,
    act.timestamp as effdt,
        (select absence_count + 1 from instrument_status
        where account_id=act.account_id
        and product_id=act.product_id
        and effdt=(
            select max(effdt) from instrument_status
            where account_id=inst.account_id
            and product_id=inst.product_id
            )
        ) as absence_count,
    run_id
    from actual_total act, product prod
    where prod.product_id=act.product_id
    and prod.data_source='HTML'
    and act.seq = (
            select max(seq) from actual_total
            where account_id=act.account_id
            and product_id=act.product_id
            )
    and status = 'A'
    and not EXISTS
            (select 1 from actual_total
            where account_id=act.account_id
            and product_id=act.product_id
            and run_id='401'
            )
    and act.run_id < 401
    """
    sql = """
    insert into instrument_status (account_id, product_id, instrument_status, effdt)
    select account_id, product_id, 'PENDING_CLOSE' as instrument_status, 
    current_timestamp as effdt,
        (select absence_count + 1 from instrument_status
        where account_id=act.account_id
        and product_id=act.product_id
        and effdt=(
            select max(effdt) from instrument_status
            where account_id=inst.account_id
            and product_id=inst.product_id
            )
        ) as absence_count,
    run_id
    from actual_total act
    where exists (
            select 1 from instrument_status inst
            where inst.account_id=act.account_id 
            and inst.product_id=act.product_id
            and inst.instrument_status in ('PENDING_CLOSE', 'CLOSED')
            and inst.effdt=(
                select max(effdt) from instrument_status
                where account_id=inst.account_id
                and product_id=inst.product_id
                )
        )
    and act.run_id=?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(sql, (run_id,))


def first_miss(run_id: int):
    """
    ready to code
    select all account/product combinations
    where data source is html
    and are not in the actual_total table for the last run
    and its current instrument status is OPEN or CLOSED

    insert a row into instrument_status with
    absence count=1, status=PENDING_CLOSE
    """
    sql = """
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(sql, (run_id,))


def second_miss(run_id: int):
    """
    For all account/web product combinations
    that is not in the actual_total table for the last run
    and its current status is pending_close

    insert a row into instrument_status with
    absence count=current absence count + 1
    """
    sql = """
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(sql, (run_id,))


def first_miss_after_close(run_id: int):
    """
    dupplicate of first_miss
    For each account/web product combination
    that is not in the actual_total table for the last run
    and its current instrument status is closed or open

    insert a row into instrument_status with
    absence count=1, status=PENDING_CLOSE
    """
    sql = """
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(sql, (run_id,))


def final_miss(run_id: int):
    """
    ready to code
    For each account/web product combination
    that is not in the actual_total table for the last run
    and its current instrument status is pending_close
    and the absence count is greater than 4

    insert a row into instrument_status with
    status of closed
    """
    sql = """
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(sql, (run_id,))


def update_instrument_status(run_id: int):
    pass
    # add_new_instruments(run_id)
    # reopen_closed_instruments(run_id)
    # first_miss(run_id)
    # second_miss
    # final_miss(run_id)


if __name__ == "__main__":
    run_id = get_last_run_id() if len(sys.argv) == 1 else int(sys.argv[1])
    update_instrument_status(run_id)
