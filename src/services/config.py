import os
import configparser
from datetime import datetime
from platform import uname


def in_wsl() -> bool:
    return 'microsoft-standard' in uname().release


config = configparser.ConfigParser()

if in_wsl():
    config_file = '/mnt/e/Google Drive/asterlan sync/config/portfolio.ini'
    category = 'wsl'
else:
    config_file = "E:\\Google Drive\\asterlan sync\\config\\portfolio.ini"
    category = 'windows'

config.read(config_file)
html_dir = config[category]['html_dir']
html_url = config['default']['html_url']
db = config[category]['db']
log_dir = config[category]['log_dir']

log_file = os.path.join(
    log_dir, f'{datetime.now().strftime("%Y-%m-%d")}.log')

html_file = os.path.join(
    log_dir, f'{datetime.now().strftime("%Y-%m-%d")}.html')

ftx_api_key = config['default']['ftx_api_key']
ftx_api_secret = config['default']['ftx_api_secret']
binance_api_key = config['default']['binance_api_key']
binance_api_secret = config['default']['binance_api_secret']
