from collections import namedtuple
from types import SimpleNamespace
from dateutil.parser import parse
import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.dict_to_object import AttrDict


def get_debts_by_product(account_id):
    sql = """
    select lo.borrower_product_id as product_id, sum(lo.amount) as amount
    from loan lo
    where lo.borrower_id=?
    and lo.status='A'
    group by lo.borrower_product_id
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, (account_id,)).fetchall()

    result = {}
    for row in rows:
        result[row.product_id] = row.amount

    return result


def max_queue_id():
    sql = """
    select max(queue_id) as queue_id
    from html_parse_queue
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql).fetchone()

    return row.queue_id


def get_last_seq():
    sql = """
    select seq, timestamp
    from actual_total act
    where seq=(
        select max(seq) from actual_total
        )
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql).fetchone()

    return row.seq, row.timestamp


def get_last_run_id():
    sql = """
    select run_id, timestamp
    from actual_total act
    where seq=(
        select max(seq) from actual_total
        )
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql).fetchone()

    return row.run_id, row.timestamp


def net_amount(amount, account_id, product_id):
    debts = get_debts_by_product(account_id)
    if product_id in debts:
        amount -= debts[product_id]
    return amount


def first_entry(account_id: int, product_id: int):
    sql = """
    select seq, run_id, timestamp, amount
    from actual_total act
    where seq=
        (select min(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    and account_id=?
    and product_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (account_id,
                        product_id,)).fetchone()

    if not row:
        return row

    amount = net_amount(row.amount, account_id, product_id)
    return AttrDict({'seq': row.seq, 'run_id': row.run_id, 'timestamp': row.timestamp, 'amount': amount})


def previous_values_days_ago(account_id: int, product_id: int, days: float):
    sql = """
    select seq, run_id, timestamp, amount
    from actual_total act
    where seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and timestamp < date('now',?))
    and account_id=?
    and product_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (f'-{days-1} days', account_id,
                        product_id,)).fetchone()

    if not row:
        return row

    amount = net_amount(row.amount, account_id, product_id)
    return AttrDict({'seq': row.seq, 'run_id': row.run_id, 'timestamp': row.timestamp, 'amount': amount})


def previous_values_by_seq(seq, account_id, product_id):
    sql = """
    select seq, run_id, timestamp, amount
    from actual_total act
    where seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and seq<?)
    and account_id=?
    and product_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (seq, account_id,
                        product_id,)).fetchone()

    if not row:
        return row

    amount = net_amount(row.amount, account_id, product_id)
    return AttrDict({'seq': row.seq, 'run_id': row.run_id, 'timestamp': row.timestamp, 'amount': amount})


def previous_values_by_run_id(run_id, account_id, product_id):
    sql = """
    select run_id, timestamp, amount
    from actual_total act
    where run_id=
        (select max(run_id) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id<?)
    and seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id
        and run_id=act.run_id)
    and account_id=?
    and product_id=?
    and act.status='A'
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        row = c.execute(sql, (run_id, account_id,
                        product_id,)).fetchone()
    if not row:
        return row

    amount = net_amount(row.amount, account_id, product_id)
    return AttrDict({'run_id': row.run_id, 'timestamp': row.timestamp, 'amount': amount})


def calc_apr(principal: float, change: float, days: float):
    if days == 0 or principal == 0:
        return 0
    years = days/365
    apr = (change/(years*principal))*100
    return apr


def to_datetime(obj):
    if type(obj).__name__ == "str":
        result = parse(obj)
    else:
        result = obj

    #log(f"to_datetime {type(obj)} {obj} = {type(result)} {result}")
    return result


def named_tuple_factory(cursor, row):
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)


def simple_namespace_factory(cursor, row):
    my_dict = {}
    index = 0
    for col in cursor.description:
        my_dict[col[0]] = row[index]
        index += 1

    result = SimpleNamespace(**my_dict)
    return result


def build_insert_statement(table_name, json_rows):
    """
    Forms an SQL insert statement from a json list of rows.
    """
    record_list = json_rows
    # create a nested list of the records' values
    values = [list(x.values()) for x in record_list]

    # get the column names
    columns = [list(x.keys()) for x in record_list][0]

    # value string for the SQL string
    values_str = ""

    # enumerate over the records' values
    for i, record in enumerate(values):

        # declare empty list for values
        val_list = []

        # append each value to a new list of values
        for v, val in enumerate(record):
            if type(val) == str:
                val = f"'{val}'"
            if val == None:
                val = 'null'
            val_list += [str(val)]

        # put parenthesis around each record string
        values_str += "(" + ', '.join(val_list) + "),\n"

    # remove the last comma and end SQL with a semicolon
    values_str = values_str[:-2] + ";"

    sql_string = "INSERT INTO %s (%s)\nVALUES %s" % (
        table_name,
        ', '.join(columns),
        values_str
    )
    # log(sql_string)
    return sql_string


def log_level(instance_id):
    return "D"


def clean_name(filename):
    """
    Removes illegal characters from file names.
    """
    filename = filename.strip().casefold()
    illegals = r'/<>:"/\|?*'
    for char in filename:
        if char in illegals:
            filename = filename.replace(char, "_")

    return filename
