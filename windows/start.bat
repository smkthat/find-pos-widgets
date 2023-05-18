@echo off

REM Получение пути до корневой директории проекта
for %%I in ("%~dp0..") do set "PROJECT_DIR=%%~fI"

REM Активация виртуальной среды
call "%PROJECT_DIR%\venv\Scripts\activate.bat"

REM Запуск скрипта
python "%PROJECT_DIR%\source\main.py"

REM Отключение виртуальной среды
deactivate
