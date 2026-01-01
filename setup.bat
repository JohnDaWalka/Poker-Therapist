@echo off
REM Quick setup script for Poker Therapist Voice Integration (Windows)

echo ==================================
echo Poker Therapist Voice Setup 🎰🎤
echo ==================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.12 or higher
    exit /b 1
)
echo ✅ Python found
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo ✅ pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt --quiet
echo ✅ Dependencies installed
echo.

REM Check for API keys
echo Checking API keys...
if "%XAI_API_KEY%"=="" if "%OPENAI_API_KEY%"=="" (
    echo ⚠️  No API keys found in environment
    echo.
    echo Please set your API keys:
    echo   set XAI_API_KEY=xai-your-key-here
    echo   set OPENAI_API_KEY=sk-your-key-here
    echo.
    echo Or create a .env file with:
    echo   XAI_API_KEY=xai-your-key-here
    echo   OPENAI_API_KEY=sk-your-key-here
    echo.
) else (
    if not "%XAI_API_KEY%"=="" echo ✅ XAI_API_KEY found
    if not "%OPENAI_API_KEY%"=="" echo ✅ OPENAI_API_KEY found
)
echo.

REM Create .streamlit directory if it doesn't exist
if not exist ".streamlit" (
    echo Creating .streamlit directory...
    mkdir .streamlit
    echo ✅ .streamlit directory created
)
echo.

REM Check if secrets.toml exists
if not exist ".streamlit\secrets.toml" (
    echo ⚠️  .streamlit\secrets.toml not found
    echo Creating from environment variables...
    
    (
        echo # Streamlit secrets file
        echo # Add your API keys here
        echo.
        echo XAI_API_KEY = "%XAI_API_KEY%"
        echo OPENAI_API_KEY = "%OPENAI_API_KEY%"
        echo.
        echo ENABLE_STREAMING = true
        echo ENABLE_THINKING = true
    ) > .streamlit\secrets.toml
    
    echo ✅ .streamlit\secrets.toml created
    echo    Please edit .streamlit\secrets.toml to add your API keys
) else (
    echo ✅ .streamlit\secrets.toml already exists
)
echo.

echo ==================================
echo Setup Complete! 🎉
echo ==================================
echo.
echo To start the application:
echo   1. Activate venv: venv\Scripts\activate.bat
echo   2. Set API keys (if not already set)
echo   3. Run: streamlit run chatbot_app.py
echo.
echo For voice features, you'll need:
echo   - XAI_API_KEY for Grok chat
echo   - OPENAI_API_KEY for voice (TTS/STT)
echo.
echo See VOICE_INTEGRATION.md for detailed setup guide
echo.
pause
