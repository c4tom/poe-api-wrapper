@echo off
setlocal enabledelayedexpansion

cls
echo.
echo ========== POE API WRAPPER INSTALLER ==========
echo [1] Install in Editable Mode (Development)
echo [2] Update from PyPI (Latest Version)
echo [3] Uninstall Package
echo [4] Clear PIP Cache
echo [5] Clean Invalid Distributions
echo.

set /p choice="Choose an option (1-5): "

if "%choice%"=="1" (
    echo Cleaning up invalid distributions...
    python -m pip cache purge
    for /d %%i in ("D:\desenv\python\Lib\site-packages\~*") do rd /s /q "%%i"
    del /q "D:\desenv\python\Lib\site-packages\~*"
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install fastapi-poe ballyregan
    python -m pip uninstall -y poe-api-wrapper
    python -m pip install --no-cache-dir --force-reinstall --no-deps poe-api-wrapper
    echo Installing in Editable Mode...
    python -m pip install --no-cache-dir -e .
)

if "%choice%"=="2" (
    echo Cleaning up invalid distributions...
    python -m pip cache purge
    for /d %%i in ("D:\desenv\python\Lib\site-packages\~*") do rd /s /q "%%i"
    del /q "D:\desenv\python\Lib\site-packages\~*"
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install fastapi-poe ballyregan
    python -m pip uninstall -y poe-api-wrapper
    python -m pip install --no-cache-dir --force-reinstall poe-api-wrapper
)

if "%choice%"=="3" (
    echo Cleaning up invalid distributions...
    python -m pip cache purge
    for /d %%i in ("D:\desenv\python\Lib\site-packages\~*") do rd /s /q "%%i"
    del /q "D:\desenv\python\Lib\site-packages\~*"
    python -m pip install --upgrade pip setuptools wheel
    python -m pip uninstall -y poe-api-wrapper
)

if "%choice%"=="4" (
    echo Clearing PIP Cache...
    python -m pip cache purge
    python -m pip install --upgrade pip setuptools wheel
)

if "%choice%"=="5" (
    echo Manually removing invalid distributions...
    python -m pip cache purge
    for /d %%i in ("D:\desenv\python\Lib\site-packages\~*") do rd /s /q "%%i"
    del /q "D:\desenv\python\Lib\site-packages\~*"
    python -m pip list
)
