#!/bin/bash
# Скрипт для запуска клиента BeautyPro

cd "$(dirname "$0")"
source venv/bin/activate
python -m client.main
