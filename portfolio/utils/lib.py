from collections import namedtuple
from types import SimpleNamespace
from dateutil.parser import parse
import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.dict_to_object import AttrDict


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


def to_datetime(obj):
    if type(obj).__name__ == "str":
        result = parse(obj)
    else:
        result = obj

    # log(f"to_datetime {type(obj)} {obj} = {type(result)} {result}")
    return result


def named_tuple_factory(cursor, row):
    fields = [col[0] for col in cursor.description]
    result_fn = namedtuple("Row", fields)
    return result_fn(*row)


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
                val = "null"
            val_list += [str(val)]

        # put parenthesis around each record string
        values_str += "(" + ", ".join(val_list) + "),\n"

    # remove the last comma and end SQL with a semicolon
    values_str = values_str[:-2] + ";"

    sql_string = "INSERT INTO %s (%s)\nVALUES %s" % (
        table_name,
        ", ".join(columns),
        values_str,
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
