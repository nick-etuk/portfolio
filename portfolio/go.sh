cd $REPO_PATH\portfolio
.venv\Scripts\python portfolio\main.py
#TODO: if ERRORLEVEL 1 .venv\Scripts\python.exe portfolio\main.py retry
.venv\Scripts\python.exe portfolio\services\backup\db.py
