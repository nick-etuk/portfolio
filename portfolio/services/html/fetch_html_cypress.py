import json
import os
import platform
import subprocess
from pathlib import Path

import sqlite3 as sl
import sys
from icecream import ic
from portfolio.utils.init import init
from portfolio.utils.lib import named_tuple_factory

from portfolio.utils.config import db, cypress_path, cypress_data_dir
from portfolio.definitions import root_dir


def fetch_html_cypress(run_id, run_mode):
    if run_mode == "normal":
        print("Fetching html with cypress...")
        if platform.system() == "Windows":
            args = [
                "pwsh.exe",
                r"C:\app\nvm\v18.20.4\npx.ps1"
            ]
        else:
            args = ["npx"]

        subprocess.call(
            args + [
                "cypress",
                "run",
                "--browser",
                "chrome",
                "--env",
                f"runId={run_id}",
            ],
            cwd=cypress_path,
        )

        # subprocess.call(
        #     [
        #         r"pwsh.exe"
        #         r"C:\app\nvm\v18.20.4\npx.ps1",
        #         "cypress",
        #         "run",
        #     ],
        #     # cwd="/Users/macbook-work/Documents/repos/portfolio/cypress",
        #     cwd=cypress_path,
        # )

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

if __name__ == "__main__":
    init()
    fetch_html_cypress(420, "normal")