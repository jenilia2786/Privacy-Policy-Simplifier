@echo off
echo ===================================================
echo     Privacy Policy Simplifier Setup & Run Script
echo ===================================================

echo Checking for virtual environment...
if not exist venv (
    echo Creating virtual environment...
    py -3.11 -m venv venv
) else (
    echo Virtual environment found.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --default-timeout=1000 -r requirements.txt

echo.
echo ===================================================
echo Starting Flask Server...
echo ===================================================
python app.py

pause
