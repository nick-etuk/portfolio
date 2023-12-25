from datetime import datetime
import subprocess
import sys

from icecream import ic
from portfolio.calc.bitquery_balances import bitquery_balances
from portfolio.calc.targets import targets
from portfolio.calc.totals import show_totals
from portfolio.calc.changes import report_changes
from portfolio.services.api.fetch_api import fetch_api
from portfolio.services.http.fetch_html_cypress import fetch_html_cypress
from portfolio.services.queue.file_based_queue import queue_html_accounts
from portfolio.services.http.html_report import create_html_report
from portfolio.services.http.parse_html import parse_html

from portfolio.utils.init import init, log
from portfolio.utils.config import db, webdriver, cypress_data_dir
from portfolio.utils.next_run_id import next_run_id


def main():
    status = ""
    if len(sys.argv) == 1:
        run_mode = "normal"
    else:
        run_mode = sys.argv[1]
    # run_mode = "retry"
    init()
    run_id, timestamp = next_run_id(run_mode)
    log(f"Run mode:{run_mode}, run_id:{run_id}")

    fetch_api(run_id, timestamp)

    status = queue_html_accounts(run_id, run_mode)
    if webdriver == "cypress":
        fetch_html_cypress(run_id)

    parse_html(run_mode)

    changes = report_changes(run_id)
    totals = show_totals("total")
    my_targets = targets()
    bitquery_balances = bitquery_balances()
    # cash_balances = {}

    html_file = create_html_report(
        changes=changes,
        totals=totals,
        targets=my_targets,
        bitquery_balances=bitquery_balances,
    )

    subprocess.Popen([r"open", html_file])

    if status == "ERROR":
        sys.exit(1)


if __name__ == "__main__":
    main()
