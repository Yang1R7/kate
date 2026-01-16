#!/bin/bash
# Скрипт для запуска сервера BeautyPro

cd "$(dirname "$0")"
source venv/bin/activate
python -m uvicorn server.main:app --reload --host 127.0.0.1 --port 8000
