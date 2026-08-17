@echo off
setlocal
cd /d %~dp0

echo ============================================
echo   MJMS - Micro Job Management System
echo ============================================
echo.

if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

endlocal
