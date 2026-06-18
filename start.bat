@echo off
echo Starting PDF to CAD Converter...

start "Backend Server" cmd /c "cd backend && .\venv\Scripts\activate && uvicorn main:app --reload --port 8000"
start "Frontend Server" cmd /c "cd frontend && npm run dev"

echo Both servers are starting up...
echo The backend will run on http://localhost:8000
echo The frontend will open in your default browser.
