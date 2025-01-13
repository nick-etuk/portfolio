
def show_usage():
    usage = """
    Arguments:
    retry               Try again to parse failed runs. Does not fetch html.
    reload              Parse the last run_id. Does not fetch html.
    reload <run_id>     Parse the given run_id. Does not fetch html.
    normal or no args   Fetch html, call APIs, generate next run_id.
    dry_run             No fetching of html, no APIs calls. Run_id = 0
    report              Generate reports only. No fetching of html, no APIs calls.
    """
    print(usage)
