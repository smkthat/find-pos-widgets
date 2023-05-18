#!/bin/bash

# Получение пути до корневой директории проекта
PROJECT_DIR="$(dirname "$(readlink -f "$0")")/.."

# Создание виртуальной среды
python -m venv "$PROJECT_DIR/venv"

# Активация виртуальной среды
source "$PROJECT_DIR/venv/bin/activate"

# Обновление установщика
python -m pip install --upgrade pip

# Установка зависимостей
python -m pip install -r "$PROJECT_DIR/source/requirements.txt"

# Отключение виртуальной среды
deactivate