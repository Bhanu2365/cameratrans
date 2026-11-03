@echo off
set ROOT=%~dp0
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo Run the setup steps in README.md first.
  pause
  exit /b 1
)
if not exist "%ROOT%frontend\node_modules" (
  echo Run npm install in the frontend folder first.
  pause
  exit /b 1
)
start "SnapQR backend" cmd /k "cd /d ""%ROOT%backend"" ^&^& .venv\Scripts\python manage.py migrate ^&^& .venv\Scripts\python manage.py runserver 0.0.0.0:8000"
timeout /t 2 /nobreak > nul
start "SnapQR dashboard" http://localhost:5173
cd /d "%ROOT%frontend"
npm run dev -- --host 0.0.0.0
