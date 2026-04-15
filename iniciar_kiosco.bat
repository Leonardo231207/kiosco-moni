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

REM Esperar a que Flask responda (max 15 segundos)
set /a intentos=0
:esperar
timeout /t 1 /nobreak >nul
curl -s -o nul -w "" http://localhost:5000 2>nul
if errorlevel 1 (
    set /a intentos+=1
    if %intentos% lss 15 (
        goto esperar
    )
)

echo.
echo Servidor listo. Abriendo navegador...
echo.

start "" http://localhost:5000

call venv\Scripts\python app.py

pause