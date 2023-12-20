import os
from datetime import datetime
import subprocess
from tabulate import tabulate
from portfolio.calc import targets
from portfolio.calc.cash_balances import get_cash_balances
from portfolio.calc.changes import report_changes
from portfolio.calc.totals import show_totals
from portfolio.utils.config import output_dir
from portfolio.utils.init import current_logfile, init
from portfolio.utils.lib import get_last_run_id
from portfolio.risks.risks import check_risks


def create_html_report(changes, totals, targets, cash_balances):
    print("totals table 2:", totals)

    simple_html = """
    <html>
    <head>
        <style> 
            table, th, td {{ border: 1px solid blue; border-collapse: collapse; font-family: Verdana, sans-serif; font-size: 1em;}}
            th, td {{ padding: 5px; }}
            body {{ font-family: Verdana, sans-serif; font-size: 0.8em;}}
        </style>
    </head>
    <body style="font:san-serif">
        <h2>Changes</h2>
        {changes_table}
        <br>
        {risk_violations}
        <br>
        <h2>Cash</h2>
        {cash_balances}
        <br>
        <h2>Totals</h2>
        {totals_table}
        <br>   
        <h2>Targets</h2>
        {targets_table}
        <br>        
        <P>Logs</p>
        {log_messages}
        <br><br>
    </body>
    </html>
    """
    html_template = simple_html

    changes_html = tabulate(
        changes, tablefmt="html", headers=["Account", "Product", "Amount", "Change"]
    )
    totals_html = tabulate(
        totals,
        tablefmt="html",
        headers=[
            "Account",
            "Product",
            "Amount",
            "Risk",
            "Chain",
            "Change",
            "Week",
            "Month",
        ],
    )
    targets_html = tabulate(
        targets,
        tablefmt="html",
        headers=["Account", "Invested", "Expected", "Current", "Shortfall"],
    )
    risk_violations = check_risks()

    cash_html = tabulate(
        cash_balances, tablefmt="html", headers=["Account", "Chain", "Symbol", "Value"]
    )

    with open(current_logfile(), "r") as f:
        log_messages = f.read()

    log_messages = log_messages.replace("\n", "<br>")
    html = html_template.replace("{{", "{")
    html = html.replace("}}", "}")
    html = html.replace("{changes_table}", changes_html)
    html = html.replace("{risk_violations}", risk_violations)
    html = html.replace("{cash_balances}", cash_html)
    html = html.replace("{totals_table}", totals_html)
    html = html.replace("{targets_table}", targets_html)
    html = html.replace("{log_messages}", log_messages)

    report_file = os.path.join(
        output_dir,
        f'portfolio_summary_{datetime.now().strftime("%Y-%m-%d")}.html',
    )
    with open(report_file, "w") as f:
        f.write(html)

    return report_file


if __name__ == "__main__":
    init()
    run_id, timestamp = get_last_run_id()
    changes_table = report_changes(run_id)
    totals_table = show_totals("total")
    print("totals table 0b:", totals_table, "\n")
    targets_table = targets()
    print("totals table 1:", totals_table, "\n")
    cash_balances = get_cash_balances()
    html_file = create_html_report(
        changes=changes_table,
        totals=totals_table,
        targets=targets_table,
        cash_balances=cash_balances,
    )

    subprocess.Popen([r"C:\Program Files\Mozilla Firefox\firefox.exe", html_file])
