import os
import configparser
from pathlib import Path
import socket
import sys
from icecream import ic
from portfolio.definitions import root_dir

"""
def in_wsl() -> bool:
    return 'microsoft-standard' in uname().release


config = configparser.ConfigParser()

if in_wsl():
    config_file = '/mnt/e/Google Drive/asterlan sync/config/portfolio.ini'
    category = 'wsl'
else:
    config_file = "E:\\Google Drive\\asterlan sync\\config\\portfolio.ini"
    category = 'windows'

"""

current_host = socket.gethostname()

ini_file_path = {
    "Evesham": r"E:\\Google Drive\\asterlan sync\\config\\portfolio.ini",
    # "Thinkpad-Dan": r"C:\\Users\\nick_\\Google Drive\\asterlan sync\\config\\portfolio.ini",
    "Thinkpad-Dan": r"C:\Users\nick_\OneDrive\data\portfolio\config\portfolio.ini",
    # "Nicholass-MacBook-Pro.local": r"/Users/macbook-work/Documents/config/portfolio.ini",
    "Nicholass-MacBook-Pro.local": r"/Users/macbook-work/Library/CloudStorage/OneDrive-Personal/data/portfolio/config/portfolio.ini",
    "DESKTOP-2022": r"C:\Users\Nick\OneDrive\data\portfolio\config\portfolio.ini",
}

config = configparser.ConfigParser()
config.read(ini_file_path[current_host])
data_dir = config[current_host]["data_dir"]
webdriver = config[current_host]["webdriver"]

db = os.path.join(data_dir, "portfolio.db")
if not os.path.exists(db):
    raise FileNotFoundError(f"sqlite database file not found at {db}")

log_dir = config[current_host]["log_dir"]
# log_file = os.path.join(log_dir, f'{datetime.now().strftime("%Y-%m-%d")}.log')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

output_dir = os.path.join(data_dir, "output_reports")
raw_html_dir = os.path.join(log_dir, "raw_html")
html_url = config["default"]["html_url"]

ftx_api_key = config["default"]["ftx_api_key"]
ftx_api_secret = config["default"]["ftx_api_secret"]
binance_api_key = config["default"]["binance_api_key"]
binance_api_secret = config["default"]["binance_api_secret"]
cmc_api_key = config["default"]["cmc_api_key"]
bitquery_api_key = config["default"]["bitquery_api_key"]
covalent_api_key = config["default"]["covalent_api_key"]
moralis_api_key = config["default"]["moralis_api_key"]
exchange_rate_api_key = config["default"]["exchange_rate_api_key"]

mysql_user = config["default"]["mysql_user"]
mysql_password = config["default"]["mysql_password"]
mysql_host = config["default"]["mysql_host"]

cypress_path = os.path.join(Path(root_dir).parent, "cypress")
cypress_data_dir = os.path.join(cypress_path, "cypress", "e2e", "data")