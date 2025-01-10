import os
from datetime import datetime
import platform
import subprocess
from tabulate import tabulate
from portfolio.calc.targets import targets
from portfolio.calc.bitquery_balances import get_bitquery_balances
from portfolio.calc.changes.report_changes import report_changes
from portfolio.calc.totals.show_totals import show_totals
from portfolio.reports.wallet_totals import get_wallet_totals
from portfolio.utils.config import output_dir
from portfolio.utils.init import current_logfile, init
from portfolio.utils.lib import get_last_run_id


def create_html_report(
    changes,
    totals_table,
    wallet_totals,
    targets,
    bitquery_balances,
    instrument_status_changes,
    risk_violations,
):
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
        <h2>Totals</h2>
        {totals_html}
        <br>
        <h2>Wallets</h2>
        {wallet_html}
        <br>
        <h2>Status Changes</h2>
        {instrument_status_changes}
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

    headers = ["Account", "Product", "Value", "Change", "Last updated"]
    changes_table = []
    for change_row in changes:
        changes_table.append(
            [
                change_row["account"],
                change_row["product"],
                round(change_row["amount"]),
                round(change_row['change']),
                # change_row['apr'],
                change_row['timespan'],
            ]
        )

    changes_html = tabulate(changes_table, tablefmt="html", headers=headers)
    # changes_html = grey_out_pending(changes_html)

    totals_working = []
    for totals_row in totals_table:
        totals_working.append(
            [
                totals_row["account"],
                totals_row["product"],
                totals_row["amount"],
                totals_row["risk"],
                totals_row["chain"],
                totals_row["last_updated"],
                totals_row['change'],
                totals_row['week'],
                totals_row['month'],
                totals_row['alltime'],
                totals_row['alltime_apr'],
            ]
        )
    totals_html = tabulate(
        totals_working,
        tablefmt="html",
        headers=[
            "Account",
            "Prouct",
            "Amount",
            "Risk",
            "Chain",
            "Last updated",
            "Change",
            "Week",
            "Month",
            "Overall",
            "Overall APR",
        ],
    )
    wallet_headers = [
        "Account",
        "Product",
        "Chain",
        "Amount",
        "Change",
        "Week",
        "Month",
        "Overall",
    ]
    wallet_working = []

    # "account": row.account,
    # "product": row.product,
    # "chain": row.chain,
    # "amount": row.amount,
    # "change": changes.last_run,
    # "weekly": changes.weekly,
    # "monthly": changes.monthly,
    # "all_time": changes.all_time,

    for wallet_row in wallet_totals:
        wallet_working.append(
            [
                wallet_row["account"],
                wallet_row["product"],
                wallet_row["chain"],
                round(wallet_row["amount"]),
                wallet_row["change"],
                wallet_row["weekly"],
                wallet_row["monthly"],
                wallet_row["alltime"],
            ]
        )

    wallet_html = tabulate(
        tabular_data=wallet_working,
        headers=wallet_headers,
        tablefmt="html",
    )

    targets_html = tabulate(
        targets,
        tablefmt="html",
        headers=["Account", "Invested", "Expected", "Current", "Shortfall"],
    )

    bitquery_html = tabulate(
        bitquery_balances,
        tablefmt="html",
        headers=["Account", "Chain", "Symbol", "Value"],
    )

    instrument_status_changes_html = tabulate(
        instrument_status_changes,
        tablefmt="html",
        headers=["Account", "Instrument", "Value", "Status", "Absence count"],
    )

    with open(current_logfile(), "r") as f:
        log_messages = f.read()

    log_messages = log_messages.replace("\n", "<br>")
    html = html_template.replace("{{", "{")
    html = html.replace("}}", "}")
    html = html.replace("{changes_table}", changes_html)
    html = html.replace("{risk_violations}", risk_violations)
    html = html.replace("{bitquery_balances}", bitquery_html)
    html = html.replace("{totals_html}", totals_html)
    html = html.replace("{wallet_html}", wallet_html)
    html = html.replace("{targets_table}", targets_html)
    html = html.replace("{log_messages}", log_messages)
    html = html.replace("{instrument_status_changes}", instrument_status_changes_html)

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
    totals = show_totals(run_id=run_id, timestamp=timestamp, totals_mode="total")
    print("totals table 0b:", totals.totals_table, "\n")
    targets_table = targets(totals)
    print("totals table 1:", totals.totals_table, "\n")
    html_file = create_html_report(
        changes=changes_table,
        totals_table=totals.totals_table,
        targets=targets_table,
        bitquery_balances=None,
        wallet_totals=get_wallet_totals(),
        instrument_status_changes=None,
        risk_violations="",
    )

    # subprocess.Popen([r"C:\Program Files\Mozilla Firefox\firefox.exe", html_file])
    if platform.system() == "Windows":
        subprocess.Popen([r"pwsh.exe", "-c", html_file], shell=True)
    else:
        subprocess.Popen([r"open", html_file])
