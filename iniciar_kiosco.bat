@echo off
chcp 65001 >nul
title Kiosco Moni

cd /d "%~dp0"

echo ==========================================
echo           KIOSCO MONI
echo ==========================================
echo.

if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        echo Asegurate de tener Python instalado.
        pause
        exit /b 1
    )
)

echo Verificando dependencias...
call venv\Scripts\pip install --upgrade -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo.
echo Iniciando Kiosco...
echo.

REM Esperar 3 segundos para que Flask levante
timeout /t 3 /nobreak >nul

start "" http://localhost:5000

call venv\Scripts\python app.py

pause
