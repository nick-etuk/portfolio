
import glob
import json
import os
from portfolio.utils.config import log_dir
from icecream import ic


def load_last_response(api_name:str, account: str, category: str):
    output_dir = os.path.join(log_dir, api_name)
    os.makedirs(output_dir, exist_ok=True)
    filespec = os.path.join(output_dir, f"{account.replace(' ','_')}_{category}_*.json")
    list_of_files = glob.glob(filespec)
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    ic(latest_file)
    with open(latest_file, "r") as f:
        response = json.loads(f.read())
    return response