G:
cd "G:\local_only\repos\portfolio"
.venv\Scripts\python.exe portfolio\main.py
if ERRORLEVEL 1 .venv\Scripts\python.exe portfolio\main.py retry
.venv\Scripts\python.exe portfolio\services\backup\db.py

