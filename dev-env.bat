@echo off
setlocal enabledelayedexpansion

:menu
cls
echo.
echo ========== POE API WRAPPER DEVELOPMENT ENVIRONMENT ==========
echo [1] Create Virtual Environment
echo [2] Activate Virtual Environment
echo [3] Install Development Dependencies
echo [4] Run Tests
echo [5] Generate Documentation
echo [6] Start Development Server
echo [7] Clean Project
echo [8] Exit
echo.

set /p choice="Choose an option (1-8): "

if "%choice%"=="1" (
    echo Creating Virtual Environment...
    python -m venv venv
    echo Virtual environment created successfully.
    pause
    goto menu
)

if "%choice%"=="2" (
    echo Activating Virtual Environment...
    call venv\Scripts\activate
    echo Virtual environment activated.
    cmd /k
    goto menu
)

if "%choice%"=="3" (
    echo Installing Development Dependencies...
    call venv\Scripts\activate
    pip install -r requirements-dev.txt
    pip install -e .
    echo Development dependencies installed.
    pause
    goto menu
)

if "%choice%"=="4" (
    echo Running Tests...
    call venv\Scripts\activate
    pytest tests/
    pause
    goto menu
)

if "%choice%"=="5" (
    echo Generating Documentation...
    call venv\Scripts\activate
    sphinx-build -b html docs docs/_build
    echo Documentation generated in docs/_build.
    pause
    goto menu
)

if "%choice%"=="6" (
    echo Starting Development Server...
    call venv\Scripts\activate
    python -m flask run
    pause
    goto menu
)

if "%choice%"=="7" (
    echo Cleaning Project...
    rmdir /s /q venv
    rmdir /s /q build
    rmdir /s /q dist
    rmdir /s /q *.egg-info
    del /q /f *.pyc
    del /q /f __pycache__
    echo Project cleaned successfully.
    pause
    goto menu
)

if "%choice%"=="8" (
    echo Exiting...
    exit /b
)

echo Invalid option. Please try again.
pause
goto menu