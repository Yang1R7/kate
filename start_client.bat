@echo off
REM Скрипт для запуска клиента BeautyPro (Windows)

cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m client.main
pause
