@echo off
REM Activate virtual environment
call venv\Scripts\activate

REM Install or update required dependencies
pip install --upgrade pip
pip install fastapi-poe ballyregan

REM Set Flask environment and run the script
set FLASK_ENV=development
python -m poe_api_wrapper.chat_web_search --database historico\historico.sqlite --dev

REM Check the exit code and pause if there's an error
if %ERRORLEVEL% neq 0 (
    echo An error occurred while running the script.
    pause
)