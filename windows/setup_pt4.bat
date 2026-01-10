@echo off
REM Setup script for JohnDaWalka's Poker Therapist
REM This script configures your environment for PT4 integration

echo ========================================
echo Poker Therapist Setup - JohnDaWalka
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Install required packages
echo Installing required packages...
pip install -q psycopg2-binary python-dotenv requests
if errorlevel 1 (
    echo [ERROR] Failed to install packages
    pause
    exit /b 1
)

echo [OK] Packages installed
echo.

REM Create .env file if it doesn't exist
if not exist backend\.env (
    echo Creating backend\.env configuration file...
    copy backend\.env.example backend\.env >nul
    echo [OK] Created backend\.env
    echo.
    echo IMPORTANT: Edit backend\.env and set:
    echo   - PT4_DB_PASSWORD: Your PokerTracker 4 database password
    echo   - PT4_PLAYER_NAME: Your poker screen name (default: jdwalka)
    echo.
    notepad backend\.env
) else (
    echo [OK] backend\.env already exists
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Quick Start Commands:
echo   1. Test PT4 connection:
echo      python windows\pt4_sync.py test
echo.
echo   2. Import recent hands:
echo      python windows\quick_start.py
echo.
echo   3. Import today's session:
echo      python windows\quick_start.py today
echo.
echo   4. Start API server:
echo      python -m backend.api.main
echo.
echo Documentation:
echo   - PT4 Integration: docs\PT4_INTEGRATION.md
echo   - WPN Support: docs\WPN_HAND_HISTORY.md
echo.
pause
