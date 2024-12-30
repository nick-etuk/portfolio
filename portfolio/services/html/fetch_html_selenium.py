from datetime import datetime
import os
import sqlite3 as sl
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from portfolio.calc.changes.change_str import change_str

from portfolio.utils.config import db, output_dir, html_url
from portfolio.utils.lib import named_tuple_factory
from portfolio.utils.init import log
from portfolio.utils.utils import first_number, pause


def fetch_html_selenium(param_row, run_id, queue_id, run_mode):
    sql = """
    select act.amount, act.timestamp
    from actual_total act
    inner join account ac
    on ac.account_id=act.account_id
    where act.account_id=?
    and act.product_id=7
    and seq=
        (select max(seq) from actual_total
        where account_id=act.account_id
        and product_id=act.product_id)
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        last_run = c.execute(sql, (param_row.account_id,)).fetchone()

    last_total = last_run.amount

    url = html_url + param_row.address
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d_%H_%M_%S")
    timestamp_str2 = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{param_row.account}_{timestamp_str}"

    sleep_time = 30 if run_mode in ["reload", "retry"] else 15

    new_total = 0
    status = "PARSING"

    chrome_options = Options()
    if run_mode not in ["reload", "retry", "normal"]:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    # driver = webdriver.Chrome(options=chrome_options, service_args=["--verbose", f"--log-path={log_dir}"])
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        # refresh_element = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CLASS_NAME, "UpdateButton_updateTimeNumber__XnaER"))
        # log(f"Sleeping for {sleep_time} seconds")
        sleep(sleep_time)

        refresh_element = driver.find_element(
            By.CSS_SELECTOR, "[class*='UpdateButton_updateTimeNumber']"
        )
        # driver.find_element(By.CLASS_NAME, "UpdateButton_updateTimeNumber__2afUS")
        refresh_text = refresh_element.text
        # log(f"Refresh button text: {refresh_text}")

        total_div = driver.find_element(
            By.CSS_SELECTOR, "[class*='HeaderInfo_totalAsset']"
        )
        # driver.find_element(By.CLASS_NAME, "HeaderInfo_totalAsset__3PC8b")
        total_text = total_div.text
        total_text = total_text.replace("$", "").replace(",", "")
        new_total = float(first_number(total_text))

        if (new_total + new_total * 0.2) < last_total:
            status = "INVALID"

        if run_mode in ["reload", "retry"] or status == "INVALID":
            driver.save_screenshot(os.path.join(output_dir, filename + ".png"))

    except Exception as e:
        msg = f"{e}"
        print(msg)
        # print full message to stdout, write truncated version to log
        log(msg[:130])
        status = "ERROR"

    change, apr = change_str(
        amount=new_total,
        timestamp=timestamp_str2,
        previous_amount=last_total,
        previous_timestamp=last_run.timestamp,
    )
    log(f"Status: {status}. New total {round(new_total)}, last total {last_total}")

    sql = """
    update html_parse_queue
    set filename = ?,
    last_total = ?,
    new_total = ?,
    status = ?,
    timestamp = ?
    where queue_id = ?
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        c.execute(
            sql,
            (filename + ".html", last_total, new_total, status, timestamp, queue_id),
        )

    page_source = driver.page_source
    with open(os.path.join(output_dir, filename + ".html"), "w") as f:
        f.write(page_source)

    driver.close()
    pause()

    return status
