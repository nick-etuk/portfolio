import os
from datetime import datetime
import subprocess
from tabulate import tabulate
from portfolio.calc import targets
from portfolio.calc.bitquery_balances import get_bitquery_balances
from portfolio.calc.changes.report_changes import report_changes
from portfolio.calc.totals import show_totals
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
        {totals_table}
        <br>
        <h2>Wallets</h2>
        {wallet_table}
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

    changes_table = []
    headers = ["Account", "Product", "Value", "Change", "Last updated"]

    for change_row in changes:
        changes_table.append(
            [
                change_row["account"],
                change_row["product"],
                round(change_row["amount"]),
                change_row['change'],
                change_row['timespan'],
            ]
        )

    changes_html = tabulate(changes_table, tablefmt="html", headers=headers)
    # changes_html = grey_out_pending(changes_html)

    totals_html = tabulate(
        totals_table,
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
    wallet_table = []

    # "account": row.account,
    # "product": row.product,
    # "chain": row.chain,
    # "amount": row.amount,
    # "change": changes.last_run,
    # "weekly": changes.weekly,
    # "monthly": changes.monthly,
    # "all_time": changes.all_time,

    # for wallet_row in wallet_totals:
    #     wallet_table.append(
    #         [
    #             wallet_row["account"],
    #             wallet_row["product"],
    #             round(wallet_row["amount"]),
    #             # wallet_row["change"],
    #         ]
    #     )

    # wallet_html = tabulate(wallet_table, tablefmt="html", headers=wallet_headers)
    wallet_table_formatted = tabulate(
        # wallet_totals, tablefmt="html", headers=wallet_headers
        wallet_totals,
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
    html = html.replace("{totals_table}", totals_html)
    html = html.replace("{wallet_table}", wallet_table_formatted)
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
    totals_table = show_totals("total")
    print("totals table 0b:", totals_table, "\n")
    targets_table = targets()
    print("totals table 1:", totals_table, "\n")
    cash_balances = get_bitquery_balances()
    html_file = create_html_report(
        changes=changes_table,
        totals_table=totals_table,
        targets=targets_table,
        bitquery_balances=cash_balances,
    )

    subprocess.Popen([r"C:\Program Files\Mozilla Firefox\firefox.exe", html_file])
