from time import sleep
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

from portfolio.utils.config import db, cypress_path, cypress_data_dir, current_host
from portfolio.definitions import root_dir


def npx_command():
    if platform.system() != "Windows":
        return ["npx"]
         
    npx_path = {
        "DESKTOP-2022": r"F:\app\nvm\v18.13.0\npx",
        "Thinkpad-Dan": r"C:\app\nvm\v18.20.4\npx.ps1",
    }

    return ["pwsh", "-c", npx_path[current_host]]


def fetch_html_cypress(run_id, run_mode):
    if run_mode == "normal":
        print("Fetching html with cypress...")
        try:
            subprocess.call(
                npx_command() + [
                    "cypress",
                    "run",
                    "--browser",
                    "chrome",
                    "--env",
                    f"runId={run_id}",
                ],
                cwd=cypress_path,
            )
        except Exception as e:
            print(f"Error fetching html with cypress: {e}")
            return "ERROR"

    status_summary = "DONE"
    status_file = os.path.join(
        cypress_data_dir, "queue", f"cypressStatus-{run_id}.json"
    )
    print(f"Waiting for {status_file}")
    wait_time = 0
    max_wait_time = 60 * 5
    interval = 10
    while not os.path.exists(status_file):
        if wait_time > max_wait_time:
            print(f"Timeout waiting for {status_file}")
            status_summary = "ERROR"
            break
        wait_time += interval
        sleep(interval)
        print(".", end="", flush=True)

    if status_summary == "ERROR":
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