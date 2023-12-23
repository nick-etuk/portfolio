import os
from datetime import datetime
from portfolio.utils.config import db, data_dir, mysql_password
import shutil


timestamp = datetime.now()
timestamp_str = timestamp.strftime("%Y-%m-%d_%H_%M_%S")
new_file_name = f"portfolio_{timestamp_str}.db"

destination_dir = os.path.join(data_dir, "db_backups")
if not os.path.exists(destination_dir):
    os.mkdir(destination_dir)

shutil.copyfile(db, os.path.join(destination_dir, new_file_name))

# db2 = "C:\\Users\\Nick\\OneDrive\\data\\serious-kid\\serious-kid.db"
# new_file_name2 = f"serious_kid_{timestamp_str}.db"
# shutil.copyfile(db2, os.path.join(destination, new_file_name2))

"""
mysql_dump = "F:\\app\\MySQL Server 8.0\\bin\\mysqldump.exe"
params = ["-u", "admin", "-p", mysql_password]

# destination = "C:\\Users\\Nick\\OneDrive\\bak"

new_file_name3 = os.path.join(
    destination, f"serious-kid-mysql_{timestamp_str}")
process = subprocess.Popen([mysql_dump, params, new_file_name3])
process.wait()

"""
