import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3 as sl
from icecream import ic
from portfolio.calculations.cash_balances import get_cash_balances
from portfolio.calculations.totals import show_totals
from portfolio.calculations.changes import report_changes
from portfolio.calculations.targets import targets
from portfolio.services.api.fetch_api import fetch_api
from portfolio.services.http.fetch_row import fetch_row
from portfolio.services.http.html_report import create_html_report
from portfolio.services.http.parse_html import parse_html
from portfolio.utils import utils

from portfolio.utils.init import init, log
from portfolio.utils.lib import max_queue_id, named_tuple_factory
from portfolio.utils.config import db
from portfolio.utils.next_run_id import next_run_id


def fetch_html(run_id, timestamp, run_mode):
    sql = """
        select ac.account_id, ac.descr as account, ac.address 
        from account ac
        where ac.address <> ' '
        """
    args = ()

    if run_mode == "reload":
        sql = """
        select q.queue_id, ac.account_id, ac.descr as account, ac.address 
        from account ac
        where ac.address <> ' '
        """
        args = ()

        if len(sys.argv) == 3:
            sql = """
            select q.queue_id, ac.account_id, ac.descr as account, ac.address 
            from account ac
            where ac.address <> ' '
            and account_id=?
            """
            account_id = sys.argv[2]
            args = (account_id,)

    if run_mode == "retry":
        sql = """
        select q.queue_id, ac.account_id, ac.descr as account, ac.address, q.status
        from account ac
        inner join html_parse_queue q
        on q.account_id=ac.account_id
        where ac.address <> ' '
        and q.status not in ('DONE','PARSING')
        """
        args = ()

    chrome_options = Options()
    if not run_mode in ["reload", "retry", "normal"]:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")

    error_found = False
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(sql, args).fetchall()

        for row in rows:
            log(f"Fetching {row.account}")

            if run_mode != "normal":
                queue_id = row.queue_id
            else:
                sql = """
                insert into html_parse_queue (run_id, account_id, filename, last_total, new_total, status, timestamp)
                values (?,?,?,?,?,?,?)
                """
                with sl.connect(db) as conn:
                    conn.row_factory = named_tuple_factory
                    c = conn.cursor()
                    c.execute(sql, (run_id, row.account_id,
                                    " ", 0, 0, "FETCHING", None))
                queue_id = max_queue_id()

            # driver = webdriver.Chrome(options=chrome_options, service_args=["--verbose", f"--log-path={log_dir}"])
            driver = webdriver.Chrome(options=chrome_options)
            status = fetch_row(row, run_id, queue_id, driver, run_mode)
            if status == 'ERROR':
                error_found = True

            driver.close()
            utils.pause()

    return "ERROR" if error_found else "PARSING"


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_mode = "normal"
    else:
        run_mode = sys.argv[1]
    #run_mode = "retry"
    init()
    run_id, timestamp = next_run_id(run_mode)
    log(f"Run mode:{run_mode}, run_id:{run_id}")

    fetch_api(run_id, timestamp)

    status = fetch_html(run_id, timestamp, run_mode)
    parse_html(run_mode)

    changes = report_changes(run_id)
    totals = show_totals("total")
    targets = targets()
    cash_balances = get_cash_balances()

    html_file = create_html_report(
        changes=changes, totals=totals, targets=targets, cash_balances=cash_balances)

    #subprocess.Popen([r"F:\app\Notepad++\notepad++.exe", current_logfile()])
    subprocess.Popen(
        [r"C:\Program Files\Mozilla Firefox\firefox.exe", html_file])

    if status == 'ERROR':
        sys.exit(1)
