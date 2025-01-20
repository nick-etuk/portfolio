.venv\Scripts\Activate.ps1
python portfolio\main.py
if ERRORLEVEL 1 .venv\Scripts\python.exe portfolio\main.py retry
.venv\Scripts\python.exe portfolio\backup\db.py
