@echo off
echo Starting Build-a-RIG in Development Mode (No OpenAI API calls)
echo.

REM Set development mode to avoid OpenAI API costs
set DEVELOPMENT_MODE=true

REM Start API server in background
echo Starting API server...
start "API Server" cmd /k "uvicorn api.index:app --reload"

REM Wait a moment for API to start
timeout /t 3 /nobreak > nul

REM Start Streamlit UI
echo Starting Streamlit UI...
streamlit run ui/app.py

pause 