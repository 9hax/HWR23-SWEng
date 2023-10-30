@echo off
echo [92mEasyFormular Instance Runner[0m

REM Upgrade pip version
py -m pip install --upgrade pip

REM Install Pip Requirements
py -m pip install -r requirements.txt

echo [92mDone Installing Libraries.[0m
echo [92mPreparing Database.[0m
py -m flask db init

echo [92mCreating Database Content.[0m

py -m flask db migrate
py -m flask db upgrade
py -m flask db migrate
py -m flask db upgrade

cls
echo [92mOpen your browser at http://localhost:8123 to access the application.[0m
echo [92mstarting up flask...[0m

py -m flask run --port=8123
