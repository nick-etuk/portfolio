import os
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read("E:\\Google Drive\\asterlan sync\\config\\portfolio.ini")
html_dir = config['default']['html_dir']
html_url = config['default']['html_url']
db = config['default']['db']
log_dir = config['default']['log_dir']

log_file = os.path.join(
    log_dir, f'{datetime.now().strftime("%Y-%m-%d")}.log')

html_file = os.path.join(
    log_dir, f'{datetime.now().strftime("%Y-%m-%d")}.html')

ftx_api_key = config['default']['ftx_api_key']
ftx_api_secret = config['default']['ftx_api_secret']
binance_api_key = config['default']['binance_api_key']
binance_api_secret = config['default']['binance_api_secret']
