@echo off

REM Получение пути до корневой директории проекта
set PROJECT_DIR=%~dp0..

REM Создание виртуальной среды
python -m venv "%PROJECT_DIR%\venv"

REM Активация виртуальной среды
call "%PROJECT_DIR%\venv\Scripts\activate.bat"

REM Обновление установщика
python -m pip install --upgrade pip

REM Установка зависимостей
python -m pip install -r "%PROJECT_DIR%\source\requirements.txt"

REM Отключение виртуальной среды
deactivate