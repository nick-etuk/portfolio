from datetime import datetime
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

from portfolio.services.api.moralis.check_moralis_for_new_protocols import check_moralis_for_new_protocols
from portfolio.services.api.moralis.wallet_token_values import moralis_wallet_token_values
from portfolio.services.html.fetch_html_cypress import fetch_html_cypress
from portfolio.services.queue.file_based_queue import queue_html_accounts
from portfolio.services.html.html_report import create_html_report
from portfolio.services.html.parse_html import parse_html

from portfolio.utils.init import error, info, init, log, warn
from portfolio.utils.config import webdriver
from portfolio.utils.next_run_id import get_timestamp, next_run_id

from portfolio.interactive.manual_balances.manual_balances import get_manual_balances
from portfolio.utils.show_usage import show_usage


def fetch_html(run_mode, run_id, reload_account=""):
    queue_html_accounts(run_id, run_mode)
    if webdriver == "cypress":
        fetch_html_cypress(run_id, run_mode)
        parse_html(run_mode, run_id, reload_account)


def fetch_data(run_mode, run_id, timestamp, reload_account=""):
    if run_mode == "normal":
        get_manual_balances(run_id, timestamp)
        fetch_api(run_mode=run_mode, run_id=run_id, timestamp=timestamp)
        moralis_wallet_token_values(run_mode=run_mode, run_id=run_id, timestamp=timestamp)
        check_moralis_for_new_protocols()
        fetch_html()

    instrument_status_changes = update_instrument_status(run_mode, run_id)
    changes = report_changes(run_id)
    totals = show_totals(run_id, timestamp, "total")
    wallet_totals = get_wallet_totals()
    # my_targets = targets(totals) #todo: fix this
    risk_violations = check_risks(totals.combined)

    html_file = create_html_report(
        changes=changes,
        totals_table=totals.totals_table,
        wallet_totals=wallet_totals,
        targets=None,
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



    # instrument_status_changes = update_instrument_status(run_mode, run_id)
    # ic(instrument_status_changes)
    # moralis_wallet_token_values(run_mode="dry_run", run_id=run_id, timestamp=timestamp)
    # sys.exit(0)

    fetch_data()
    # if any ERROR messages for the current run_id, exit with error status
