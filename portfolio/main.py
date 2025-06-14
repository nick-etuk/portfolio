
from datetime import datetime
import sys
from portfolio.services.fetch_data import fetch_data
from portfolio.utils.init import error, init, log, warn
from portfolio.utils.next_run_id import get_timestamp, next_run_id
from portfolio.utils.show_usage import show_usage

if __name__ == "__main__":
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

    if not timestamp:
        warn(f"No timestamp found for {run_id}. Using current timestamp {timestamp}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    init(run_id)
    log(f"Run mode {run_mode}, run_id {run_id}")
    fetch_data(run_mode, run_id, timestamp, reload_account)
