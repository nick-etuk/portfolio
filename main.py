import subprocess
import sys

from icecream import ic
from portfolio.calc.bitquery_balances import get_bitquery_balances
from portfolio.calc.instrument_status.update_status import update_instrument_status
from portfolio.calc.targets import targets
from portfolio.calc.totals import show_totals
from portfolio.calc.changes import report_changes
from portfolio.risks.risks import check_risks
from portfolio.services.api.fetch_api import fetch_api
from portfolio.services.api.covalent_api_generic import test_api
from portfolio.services.http.fetch_html_cypress import fetch_html_cypress
from portfolio.services.queue.file_based_queue import queue_html_accounts
from portfolio.services.http.html_report import create_html_report
from portfolio.services.http.parse_html import parse_html

from portfolio.utils.init import init, log
from portfolio.utils.config import db, webdriver, cypress_data_dir
from portfolio.utils.next_run_id import next_run_id


def main():
    status = ""
    fetch_api(run_id, timestamp)

    status = queue_html_accounts(run_id, run_mode)
    if webdriver == "cypress":
        fetch_html_cypress(run_id, run_mode)

    parse_html(run_mode, reload_run_id, reload_account)
    instrument_status_changes = update_instrument_status(run_id)
    changes = report_changes()
    totals = show_totals("total")
    # totals = show_totals("cash")
    my_targets = targets()
    bitquery_balances = get_bitquery_balances(run_mode)
    risk_violations = check_risks()

    html_file = create_html_report(
        changes=changes,
        totals=totals,
        targets=my_targets,
        bitquery_balances=bitquery_balances,
        instrument_status_changes=instrument_status_changes,
        risk_violations=risk_violations,
    )

    subprocess.Popen([r"open", html_file])

    if status == "ERROR":
        sys.exit(1)


if __name__ == "__main__":
    init()
    test_api()
    sys.exit(0)

    args_len = len(sys.argv)
    if args_len == 1:
        run_mode = "normal"
    elif args_len > 1:
        run_mode = sys.argv[1]

    run_id, timestamp = next_run_id(run_mode)

    reload_run_id = None
    if args_len == 3:
        reload_run_id = sys.argv[2]
        run_id = reload_run_id

    reload_account = None
    if args_len == 4:
        reload_account = sys.argv[3]

    log(f"Run mode:{run_mode}, run_id:{run_id}")
    # main()
