Set-Location $CURRENT_PROJECT_ROOT
writedebug "=>fetch-data.ps1: Current Directory: $(Get-Location)"
.\.venv_portfolio\Scripts\Activate.ps1
# .venv\Scripts\python.exe portfolio\main.py fetch
python portfolio\main.py fetch
