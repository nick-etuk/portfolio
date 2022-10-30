import os
from config import db, log_dir, log_file
from datetime import datetime
import logging
import sqlite3 as sl
from lib import named_tuple_factory


class MyLogger():
    def __init__(self):
        logger = None

    current_logfile = ""


my_logger = MyLogger()


def init():
    my_logger.logger = logging.getLogger('simple_example')
    my_logger.logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    formatter = logging.Formatter('%(asctime)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    ch.setFormatter(formatter)
    my_logger.logger.addHandler(ch)

    fh = logging.FileHandler(log_file)
    my_logger.current_logfile = log_file

    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    my_logger.logger.addHandler(fh)


def current_logfile():
    return my_logger.current_logfile


def log(summary: str, details: str = "", seq: int = 0):
    # logging.info(msg)
    msg = summary + " " + details if details else summary
    my_logger.logger.info(msg)

    if seq:
        sql = """
        select seq 
        from log_once
        where summary=?
        and seq = ?
        """
        with sl.connect(db) as conn:
            conn.row_factory = named_tuple_factory
            c = conn.cursor()
            row = c.execute(sql, (summary, seq)).fetchone()

        if row:
            my_logger.logger.warn(f"{summary} already logged for #{seq}")
        else:
            sql = """
            insert into log_once(summary, seq) 
            values (?,?)
            """
            with sl.connect(db) as conn:
                c = conn.cursor()
                c.execute(sql, (summary, seq))
