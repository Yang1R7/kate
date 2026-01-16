@echo off
REM Скрипт для запуска сервера BeautyPro (Windows)

cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m uvicorn server.main:app --reload --host 127.0.0.1 --port 8000
pause
