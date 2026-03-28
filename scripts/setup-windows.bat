@echo off
REM Shark Windows Setup Script (Batch version)
REM This script provides a simple setup for environments that don't have PowerShell

echo ===============================================================
echo           Shark Windows Setup Script
echo           Setting up development environment...
echo ===============================================================
echo.

echo [1/5] Checking Windows version...
ver
echo   OK: Windows version checked
echo.

echo [2/5] Checking Git installation...
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERROR: Git not found! Please install Git for Windows from https://git-scm.com/download/win
    exit /b 1
)
git --version
echo   OK: Git is installed
echo.

echo [3/5] Configuring Git settings...
git config --local core.autocrlf true
git config --local core.symlinks false
echo   OK: Git configured for Windows
echo.

echo [4/5] Checking directory...
echo   Current directory: %CD%
echo   Username: %USERNAME%
echo   Computer: %COMPUTERNAME%
echo.

echo [5/5] Setup complete!
echo.
echo ===============================================================
echo   Windows environment setup complete!
echo.
echo   Next steps:
echo   1. Review docs\WINDOWS_SETUP.md for detailed information
echo   2. Install required development tools
echo   3. Start developing!
echo ===============================================================
echo.

pause
