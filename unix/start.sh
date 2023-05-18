#!/bin/bash

# Получение пути до корневой директории проекта
PROJECT_DIR="$(dirname "$(readlink -f "$0")")/.."

# Активация виртуальной среды
source "$PROJECT_DIR/venv/bin/activate"

# Запуск скрипта
python "$PROJECT_DIR/source/main.py"

# Отключение виртуальной среды
deactivate