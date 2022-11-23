import subprocess
from tabulate import tabulate
from changes import report_changes
from config import html_file
from init import current_logfile, init
from lib import get_last_run_id
from risks import check_risks
from totals import show_totals
from targets import targets


def create_html_report(changes, totals, targets):
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
        <P>Changes</p>
        {changes_table}
        <br>
        {risk_violations}
        <br>
        <P>Totals</p>
        {totals_table}
        <br>   
        <P>Targets</p>
        {targets_table}
        <br>        
        <P>Logs</p>
        {log_messages}
        <br><br>
    </body>
    </html>
    """
    html_template = simple_html

    changes_html = tabulate(changes, tablefmt="html", headers=[
                            'Account', 'Product', 'Amount', 'Change'])
    totals_html = tabulate(totals, tablefmt="html", headers=['Account', 'Product', 'Amount', 'Risk', 'Chain', 'Change', 'Week', 'Month']
                           )
    targets_html = tabulate(targets, tablefmt="html", headers=['Account', 'Invested', 'Expected', 'Current', 'Shortfall']
                            )
    risk_violations = check_risks()

    with open(current_logfile(), 'r') as f:
        log_messages = f.read()

    log_messages = log_messages.replace("\n", "<br>")
    html = html_template.replace('{{', '{')
    html = html.replace('}}', '}')
    html = html.replace('{changes_table}', changes_html)
    html = html.replace('{risk_violations}', risk_violations)
    html = html.replace('{totals_table}', totals_html)
    html = html.replace('{targets_table}', targets_html)
    html = html.replace('{log_messages}', log_messages)

    with open(html_file, 'w') as f:
        f.write(html)

    return html_file


if __name__ == "__main__":
    init()
    run_id, timestamp = get_last_run_id()
    changes_table = report_changes(run_id)
    totals_table = show_totals("total")
    print("totals table 0b:", totals_table, "\n")
    targets_table = targets()
    print("totals table 1:", totals_table, "\n")

    html_file = create_html_report(
        changes=changes_table, totals=totals_table, targets=targets_table)

    subprocess.Popen(
        [r"C:\Program Files\Mozilla Firefox\firefox.exe", html_file])
