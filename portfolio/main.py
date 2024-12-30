import platform
import subprocess
import sys

from icecream import ic
from portfolio.calc.instrument_status.update_status import update_instrument_status
from portfolio.calc.targets import targets
from portfolio.calc.totals.show_totals import show_totals
from portfolio.calc.changes.report_changes import report_changes
from portfolio.reports.wallet_totals import get_wallet_totals
from portfolio.risks.risks import check_risks
from portfolio.services.api.fetch_api import fetch_api

from portfolio.services.api.moralis.check_moralis_for_new_protocols import (
    check_moralis_for_new_protocols,
)
from portfolio.services.api.moralis.wallet_token_values import (
    moralis_wallet_token_values,
)
from portfolio.services.html.fetch_html_cypress import fetch_html_cypress
from portfolio.services.queue.file_based_queue import queue_html_accounts
from portfolio.services.html.html_report import create_html_report
from portfolio.services.html.parse_html import parse_html

from portfolio.utils.init import error, info, init, log
from portfolio.utils.config import webdriver
from portfolio.utils.next_run_id import get_timestamp, next_run_id

from portfolio.interactive.manual_balances.manual_balances import get_manual_balances
from portfolio.utils.utils import show_usage


def fetch_html():
    queue_html_accounts(run_id, run_mode)
    if webdriver == "cypress":
        fetch_html_cypress(run_id, run_mode)
        parse_html(run_mode, run_id, reload_account)


def main():
    if run_mode != "report":
        get_manual_balances(run_id, timestamp)
        fetch_api(run_mode=run_mode, run_id=run_id, timestamp=timestamp)
        fetch_html()
        moralis_wallet_token_values(
            run_mode=run_mode, run_id=run_id, timestamp=timestamp
        )
        check_moralis_for_new_protocols()

    instrument_status_changes = update_instrument_status(run_mode, run_id)
    changes = report_changes(run_id)
    totals = show_totals(run_id, timestamp, "total")
    # totals = show_totals("cash")
    wallet_totals = get_wallet_totals()
    my_targets = targets(totals)
    # bitquery_balances = get_bitquery_balances(run_mode) todo: fix this
    risk_violations = check_risks(totals.combined)

    html_file = create_html_report(
        changes=changes,
        totals_table=totals.totals_table,
        wallet_totals=wallet_totals,
        targets=my_targets,
        # bitquery_balances=bitquery_balances,
        bitquery_balances="",
        instrument_status_changes=instrument_status_changes,
        risk_violations=risk_violations,
    )

    if platform.system() == "Windows":
        subprocess.Popen([r"pwsh.exe", "-c", html_file], shell=True)
    else:
        subprocess.Popen([r"open", html_file])

    # if status == "ERROR":        sys.exit(1)


if __name__ == "__main__":
    # init(415)
    # changes = report_changes(415)
    # ic(changes)
    # sys.exit(0)

    args_len = len(sys.argv)
    if args_len == 1:
        run_mode = "normal"
    elif args_len > 1:
        args_list = ["normal", "retry", "reload", "dry_run", "report"]
        if sys.argv[1] not in args_list:
            error(f"Invalid argument: {sys.argv[1]}")
            show_usage()
            sys.exit(1)

        run_mode = sys.argv[1]

    run_id, timestamp = next_run_id(run_mode)
    if args_len >= 3:
        run_id = sys.argv[2]
        timestamp = get_timestamp(run_id)

    reload_account = ""
    if args_len == 4:
        reload_account = sys.argv[3]

    init(run_id)
    log(f"Run mode {run_mode}, run_id {run_id}")

    # instrument_status_changes = update_instrument_status(run_mode, run_id)
    # ic(instrument_status_changes)
    # moralis_wallet_token_values(run_mode="dry_run", run_id=run_id, timestamp=timestamp)
    # sys.exit(0)

    main()
    # if any ERROR messages for the current run_id, exit with error status
