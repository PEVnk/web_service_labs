@echo off
echo Starting Flask Image Blender Application on Windows...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Create necessary directories
if not exist "static\uploads" mkdir static\uploads
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js

:: Set environment variables
set FLASK_APP=some_app.py
set FLASK_ENV=development

echo Starting Flask application...
echo Open http://localhost:5000 in your browser
echo Press Ctrl+C to stop the application

:: Run the application
python some_app.py

:: Deactivate virtual environment when done
deactivate
echo Application stopped.
pause
