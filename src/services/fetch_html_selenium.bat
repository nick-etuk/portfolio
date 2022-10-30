G:
cd "G:\local_only\repos\portfolio"
.venv\Scripts\python.exe src\services\fetch_html_selenium.py
if ERRORLEVEL 1 .venv\Scripts\python.exe src\services\fetch_html_selenium.py retry
.venv\Scripts\python.exe src\services\backup_db.py

