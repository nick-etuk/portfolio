Portfolio tracker for cryto assets

Generates a HTML page summarising your crypt currency assets.

Saves the current value of your crypto assets in an SQLite database.

Run it every day to keep a history of how your assets are growing or shrinking.

# Installation

# Windows Installation
## Install pyenv

cd f:\app
md pyenv

Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

pyenv --version

pyenv install 3.9.6
pyenv global 3.9.6

python -c "import sys; print(sys.executable)"

python.exe -m pip install --upgrade pip

cd f:\repos\portfolio
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r portfolio\requirements.txt

pip install -e .
