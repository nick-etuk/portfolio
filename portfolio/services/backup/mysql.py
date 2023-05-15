import os
import subprocess
import time
import datetime
import pipes
from portfolio.utils.config import mysql_password
from icecream import ic


def backup_mysql_db():
    # MySQL database details to which backup to be done. Make sure below user having enough privileges to take databases backup.
    # To take multiple databases backup, create any file like /backup/dbnames.txt and put databases names one on each line and assigned to DB_NAME variable.

    DB_HOST = 'localhost'
    DB_USER = 'admin'
    DB_USER_PASSWORD = mysql_password
    #DB_NAME = '/backup/dbnameslist.txt'
    DB_NAME = 'default_schema'
    BACKUP_PATH = "C:\\Users\\Nick\\OneDrive\\bak\\mysql"

    # Getting current DateTime to create the separate backup folder like "20180817-123433".
    DATETIME = time.strftime('%Y%m%d-%H%M%S')
    TODAYBACKUPPATH = os.path.join(BACKUP_PATH, DATETIME)

    # Checking if backup folder already exists or not. If not exists will create it.
    try:
        os.stat(TODAYBACKUPPATH)
    except:
        os.mkdir(TODAYBACKUPPATH)

    # Code for checking if you want to take single database backup or assinged multiple backups in DB_NAME.
    print("checking for databases names file.")
    if os.path.exists(DB_NAME):
        file1 = open(DB_NAME)
        multi = 1
        print("Databases file found...")
        print("Starting backup of all dbs listed in file " + DB_NAME)
    else:
        # print("Databases file not found...")
        print("Starting backup of database " + DB_NAME)
        multi = 0

    # Starting actual database backup process.
    if multi:
        in_file = open(DB_NAME, "r")
        flength = len(in_file.readlines())
        in_file.close()
        p = 1
        dbfile = open(DB_NAME, "r")

        while p <= flength:
            db = dbfile.readline()   # reading database name from file
            db = db[:-1]         # deletes extra line
            dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + \
                " " + db + " > " + \
                pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
            os.system(dumpcmd)
            gzipcmd = "gzip " + \
                pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
            os.system(gzipcmd)
            p = p + 1
        dbfile.close()
    else:
        db = DB_NAME
        dumpcmd = "F:\\app\\MySQL Server 8.0\\bin\\mysqldump.exe"
        args = "-u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + \
            db + " > " + os.path.join(TODAYBACKUPPATH, db + ".sql")
        print(dumpcmd)
        # os.system(dumpcmd)
        process = subprocess.Popen([dumpcmd, args])
        process.wait()
        gzipcmd = "tar.exe -a -c -f " + \
            pipes.quote(TODAYBACKUPPATH) + "\\" + db + ".sql"
        # os.system(gzipcmd)

        print("")
        print("Backup script completed")
        print("Your backups have been created in '" +
              TODAYBACKUPPATH + "' directory")


if __name__ == "__main__":
    backup_mysql_db()
