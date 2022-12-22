import os
from datetime import datetime
from config import db
import shutil

timestamp = datetime.now()
timestamp_str = timestamp.strftime("%Y-%m-%d_%H_%M_%S")
new_file_name = f"portfolio_{timestamp_str}.db"

destination = "C:\\Users\\Nick\\OneDrive\\bak"

shutil.copyfile(db, os.path.join(destination, new_file_name))

db2 = "C:\\Users\\Nick\\OneDrive\\data\\serious-kid\\serious_kid.db"
new_file_name2 = f"serious_kid_{timestamp_str}.db"
shutil.copyfile(db2, os.path.join(destination, new_file_name2))
