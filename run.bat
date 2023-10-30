@echo off
echo "EasyFormular Instance Runner"

REM Upgrade pip version
py -m pip install --upgrade pip

REM Install Pip Requirements
py -m pip install -r requirements.txt

cls

echo Done Installing Libraries.
echo.
echo Preparing Database.
py -m flask db init

echo Creating Database Content.
py -m flask db migrate
py -m flask db upgrade
py -m flask db migrate
py -m flask db upgrade

cls

echo Run the web Server...
echo Open your browser at http://localhost:8123 to access the application.

echo starting up flask...

py -m flask run --port=8123
