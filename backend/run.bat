@echo off
echo 🩺 Starting Vet Transcription Backend Setup...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org/downloads
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        echo Try: pip install virtualenv
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python dependencies...
echo This may take 5-10 minutes on first run...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    echo Check your internet connection and try again
    pause
    exit /b 1
)

REM Create models directory
if not exist "models" mkdir models

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%

echo.
echo 🚀 Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload