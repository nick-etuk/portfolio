import json
import os
import subprocess
import sys

import sqlite3 as sl
from icecream import ic
from portfolio.calc.cash_balances import get_cash_balances
from portfolio.calc.totals import show_totals
from portfolio.calc.changes import report_changes
from portfolio.calc.targets import targets
from portfolio.services.api.fetch_api import fetch_api
from portfolio.services.queue.file_based_queue import queue_html_accounts
from portfolio.services.queue.queue_row import queue_row
from portfolio.services.http.html_report import create_html_report
from portfolio.services.http.parse_html import parse_html

from portfolio.utils.init import init, log
from portfolio.utils.lib import max_queue_id, named_tuple_factory
from portfolio.utils.config import db, webdriver, cypress_data_dir
from portfolio.utils.next_run_id import next_run_id


def fetch_html_cypress(run_id):
    print("Fetching html with cypress...")
    subprocess.call(
        ["npx", "cypress", "run", "--env", f"runId={run_id}"],
        cwd="/Users/macbook-work/Documents/repos/portfolio/cypress",
    )

    status_summary = "DONE"
    status_file = os.path.join(cypress_data_dir, f"cypressStatus-{run_id}.json")
    if not os.path.exists(status_file):
        status_summary = "ERROR"
        sql = """
        update html_parse_queue
        set status = 'ERROR'
        where run_id = ?
        """
        with sl.connect(db) as conn:
            conn.row_factory = named_tuple_factory
            c = conn.cursor()
            c.execute(sql, (run_id,))

        return status_summary

    with open(status_file, "r") as f:
        data = f.read()

    account_status_array = json.loads(data)
    for account in account_status_array:
        ic(account)
        if account["status"] == "ERROR":
            status_summary = "ERROR"

        sql = """
        update html_parse_queue
        set filename = ?,
        last_total = ?,
        new_total = ?,
        status = ?,
        timestamp = ?
        where queue_id = ?
        """
        with sl.connect(db) as conn:
            conn.row_factory = named_tuple_factory
            c = conn.cursor()
            c.execute(
                sql,
                (
                    account["fileName"],
                    account["lastTotal"],
                    0,
                    account["status"],
                    account["timestamp"],
                    account["queueId"],
                ),
            )
    return status_summary
