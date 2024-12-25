from portfolio.utils.config import config
import time
import random
import logging
from datetime import datetime
from portfolio.utils.init import log
import re


def pause():
    random.seed(datetime.now())
    # log = logging.getLogger(__name__)
    # sleep for between 5 and ten seconds between each request
    pause_length = random.randint(10, 20)
    # log(f"Sleeping for {pause_length} seconds")
    # log(f"Sleeping for {pause_length} seconds")

    time.sleep(pause_length)


def long_pause():
    # log = logging.getLogger(__name__)
    # sleep for between 5 and ten minutes between each brand
    if config.debug_local_files_only:
        return
    pause_length = random.randint(5 * 60, 10 * 60)
    mins = round(pause_length / 60, 1)
    log(f"Waiting for {mins} minutes")
    time.sleep(pause_length)


def first_number(str: str):
    result = None
    # numbers = re.findall(r"\d+", str)
    numbers = re.findall(r"\d+\.?\d*", str)
    if numbers:
        result = numbers[0]

    return result


def short_pause():
    # log = logging.getLogger(__name__)
    # sleep for between 5 and ten seconds between each request
    if config.debug_local_files_only:
        return
    pause_length = 10
    # log(f"Sleeping for {pause_length} seconds")
    time.sleep(pause_length)


def show_usage():
    usage = """
    Arguments:
    retry               Try again to parse failed runs. Does not fetch html.
    reload              Parse the last run_id. Does not fetch html.
    reload <run_id>     Parse the given run_id. Does not fetch html.
    normal or no args   Fetch html, call APIs, generate next run_id.
    dry_run             No fetching of html, no APIs calls. Run_id = 0
    """
    print(usage)


if __name__ == "__main__":
    print(first_number(r"could not convert string to float: '13607\n+0.03%'"))
