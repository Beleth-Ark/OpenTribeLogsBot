cd /d %~dp0
python -m venv env
.\env\Scripts\pip install -r requirements.txt
.\env\Scripts\python .\bot\main.py