import json
import os
import subprocess
import sqlite3 as sl
from icecream import ic
from portfolio.utils.lib import named_tuple_factory
from portfolio.utils.config import db, cypress_data_dir


def fetch_html_cypress(run_id, run_mode):
    if run_mode == "normal":
        print("Fetching html with cypress...")
        subprocess.call(
            [
                "npx",
                "cypress",
                "run",
                "--browser",
                "chrome",
                "--env",
                f"runId={run_id}",
            ],
            # ["npx", "cypress", "run", "--env", f"runId={run_id}"],
            cwd="/Users/macbook-work/Documents/repos/portfolio/cypress",
        )

    status_summary = "DONE"
    status_file = os.path.join(
        cypress_data_dir, "queue", f"cypressStatus-{run_id}.json"
    )
    if not os.path.exists(status_file):
        print(f"Error: Could not find cypress status file {status_file}")
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
        # ic(account)
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
